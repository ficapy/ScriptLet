package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	pdf "github.com/SebastiaanKlippert/go-wkhtmltopdf"
	"github.com/hhrutter/pdfcpu/pkg/api"
	"github.com/tidwall/gjson"
	"io/ioutil"
	"net/http"
	"net/http/cookiejar"
	"os"
	"sort"
	"strconv"
	"strings"
	"sync"
)

var client *http.Client

type FileIndex struct {
	Path  string
	Index int
}

var (
	allFile = []FileIndex{}
	Cid     = flag.String("cid", "", "article cid")
	User    = flag.String("user", "", "login cellphone")
	Pwd     = flag.String("pwd", "", "login password")
)

func printUsage() {
	fmt.Println("Usage of ./g_crawler:")
	flag.PrintDefaults()
}

func init() {
	flag.Parse()
	if *Cid == "" {
		printUsage()
		panic("-cid required")
	}
	if *User == "" {
		printUsage()
		panic("-user required")
	}
	if *Pwd == "" {
		printUsage()
		panic("-pwd required")
	}
	var err error
	client = &http.Client{}

	jar, err := cookiejar.New(nil)
	if err != nil {
		panic(err)
	}
	client.Jar = jar
}

func Login() {
	url := "https://account.geekbang.org/account/ticket/login"

	jsonValue, _ := json.Marshal(map[string]interface{}{
		"country":   86,
		"cellphone": *User,
		"password":  *Pwd,
		"captcha":   "",
		"remember":  1,
		"platform":  3,
		"appid":     1,
	})
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonValue))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Referer", "https://account.geekbang.org/signin")
	req.Header.Set("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")

	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	x, _ := ioutil.ReadAll(resp.Body)
	result := gjson.Get(string(x), "code").Int()
	if result != 0 {
		fmt.Println(string(x))
		panic("Login Failed")
	}
}

func getarticles() (ret []int) {
	url := "https://time.geekbang.org/serv/v1/column/articles"
	jsonValue, _ := json.Marshal(map[string]interface{}{
		"cid":    *Cid,
		"order":  "earliest",
		"prev":   "0",
		"sample": true,
		"size":   300,
	})

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonValue))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Referer", "https://account.geekbang.org/signin")
	req.Header.Set("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")

	if err != nil {
		panic(err)
	}

	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	x, _ := ioutil.ReadAll(resp.Body)
	result := gjson.Get(string(x), "data.list.#.id")
	for _, name := range result.Array() {
		ret = append(ret, int(name.Int()))
	}
	return ret
}

func getOnePage(id int, order int, ch chan int, wg *sync.WaitGroup) {
	defer func() {
		<-ch
		wg.Done()
	}()

	url := "https://time.geekbang.org/serv/v1/article"
	jsonValue, _ := json.Marshal(map[string]interface{}{
		"id":                strconv.Itoa(id),
		"include_neighbors": true,
	})
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonValue))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Referer", "https://account.geekbang.org/signin")
	req.Header.Set("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")

	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	x, _ := ioutil.ReadAll(resp.Body)
	html := gjson.Get(string(x), "data.article_content").String()
	pdfg, err := pdf.NewPDFGenerator()
	if err != nil {
		panic(err)
	}
	p := pdf.NewPageReader(strings.NewReader(`<link href=https://static001.geekbang.org/static/time/css/app.3e04e644962ca8c2f97ec7731bb7710c.css rel=stylesheet>` + html))
	p.CustomHeader.Set("Accept-Encoding", "gzip")
	p.Encoding.Set("UTF-8")
	pdfg.AddPage(p)
	pdfg.Dpi.Set(600)
	err = pdfg.Create()
	if err != nil {
		panic(err)
	}

	if _, err := os.Stat("/tmp/pdf/"); os.IsNotExist(err) {
		os.Mkdir("/tmp/pdf/", 0700)
	}

	path := "/tmp/pdf/" + fmt.Sprintf("%03d", order) + ".pdf"
	err = pdfg.WriteFile(path)

	if err != nil {
		panic(err)
	}
	allFile = append(allFile, FileIndex{
		Path:  path,
		Index: order,
	})
}

func Merge() {
	// gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=all.pdf *.pdf
	output := "test.pdf"
	allInput := []string{}
	sort.Slice(allFile, func(i, j int) bool {
		return allFile[i].Index < allFile[j].Index
	})

	for _, i := range allFile {
		allInput = append(allInput, i.Path)
	}
	fmt.Println(allInput)
	r, err := api.Merge(&api.Command{
		Mode:    0,
		InFiles: allInput,
		OutFile: &output,
	})
	if err != nil {
		panic(err)
	}
	fmt.Println(r)
}

func main() {

	Login()
	ret := getarticles()
	limitCon := make(chan int, 10)
	var wg sync.WaitGroup
	defer close(limitCon)

	for index, i := range ret {
		wg.Add(1)
		limitCon <- 1
		go getOnePage(i, index, limitCon, &wg)
	}
	wg.Wait()
	//Merge()

}

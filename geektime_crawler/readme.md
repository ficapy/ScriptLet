### geekbang 爬虫

该网站几乎没有反爬虫措施,所以很容易得到内容

#### 使用

go build

./binary --help  查看帮助

#### 其他

不同于使用selenium进行爬取，此程序直接请求api得到内容速度更快，
每一篇文章使用wkhtmltopdf进行html渲染得到pdf,最后将所有pdf合并
因为golang的pdf库功能不全(合并的时候无法保留书签), 因此使用ghostscript替代

```bash
 gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=all.pdf *.pdf
```

仅在osx下进行测试，需要先安装wkhtmltopdf
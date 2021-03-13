package main

import (
	"fmt"
	"github.com/atotto/clipboard"
	"strings"

	"github.com/go-vgo/robotgo"
	hook "github.com/robotn/gohook"
)

func main() {
	// 本脚本原意为辅助翻译配置文件编写
	// 监控command + c 事件
	// 将文本开头的 # 去掉
	// 将多行文本转化为单行文本
	// 写入粘贴板
	add()
}

func handleString(s string) string {
	all := strings.Split(s, "\n")
	var t []string
	for _, i := range all {
		i = strings.TrimSpace(i)
		if strings.HasPrefix(i, "#") {
			i = i[1:]
		}
		i = strings.TrimSpace(i)
		t = append(t, i)
	}
	ret := strings.Join(t, " ")
	if len(ret) > 20{
		fmt.Println(ret[:20])
	}else{
		fmt.Println(ret)
	}
	return ret
}

func add() {
	fmt.Println("--- monitor clipboard---")
	robotgo.EventHook(hook.KeyDown, []string{"command", "c"}, func(e hook.Event) {
		raw, err := clipboard.ReadAll()
		if err != nil {
			fmt.Println("read error")
			return
		}
		final := handleString(raw)
		err = clipboard.WriteAll(final)
		if err != nil {
			fmt.Println("write error")
			return
		}
	})

	s := robotgo.EventStart()
	<-robotgo.EventProcess(s)
}

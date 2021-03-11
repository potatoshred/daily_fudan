# Daily_Fudan
> 一键平安复旦小脚本
> 

> 无用的前情提要：https://zhuanlan.zhihu.com/p/136340395
>
>


---

## 💭声明
一眨眼过了一年，没想到时至今日还要填这个煞笔玩意，呵呵呵。


> 🔺 此脚本原理是拉取你上一次提交的信息，然后再次上传。所以跟你前一天信息一样，如果你需要修改，请停止此脚本运行，并手动提交。
> 

> 🛑 由于本人水平零蛋， 此脚本能跑起来属实意外，本人怀着探讨的目的上传到网络平台交流，并未授权任何人，造成的一切后果概不负责。


这个人很懒，此Readme文档直接拿[genshin-impact-helper](https://github.com/y1ndan/genshin-impact-helper)
改的

## 📐部署
<details>
<summary>查看教程</summary>

- 项目地址：[github/daily_fudan](https://github.com/k652/daily_fudan)
- 点击右上角`Fork`到自己的账号下

![fork](https://i.loli.net/2020/10/28/qpXowZmIWeEUyrJ.png)

- 将仓库默认分支设置为 master 分支


### 3. 添加 账号密码 至 Secrets

- 回到项目页面，依次点击`Settings`-->`Secrets`-->`New secret`

![new-secret.png](https://i.loli.net/2020/10/28/sxTuBFtRvzSgUaA.png)

- 建立名为`FUDAN`的 secret，值为`学号`+`(空格)`+`密码`，最后点击`Add secret`

- secret名字必须为`FUDAN`！
- secret名字必须为`FUDAN`！
- secret名字必须为`FUDAN`！

### 4. 启用 Actions

> Actions 默认为关闭状态，Fork 之后需要手动执行一次，若成功运行其才会激活。

返回项目主页面，点击上方的`Actions`，再点击左侧的`Daily Fudan`，再点击`Run workflow`
    
![run](https://i.loli.net/2020/10/28/5ylvgdYf9BDMqAH.png)

</details>

至此，部署完毕。

## 🔍结果

当你完成上述流程，可以在`Actions`页面点击`Daily Fudan`-->`build`-->`Run sign`查看结果。

<details>
<summary>查看结果</summary>

### 签到成功

如果成功，会输出类似`成功`的信息：


### 签到失败

如果失败，会输出类似`啥`的信息：


同时你会收到一封来自GitHub、标题为`Run failed: Daily Fudan - master`的邮件。

</details>








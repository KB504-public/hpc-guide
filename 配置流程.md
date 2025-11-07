### 准备工作

1. 首先按照 [高性能计算平台开户操作说明](https://hpc.uestc.edu.cn/customer/masterpage/masterpage.html#/model/twogradepage/newsdetail?id=15&LMBH=25&t=0.10336039533438779) 的说明，申请加入老师课题组，这样才可以正常的使用 GPU 资源。
2. 然后按照 [高性能计算专用VPN工具](https://hpc.uestc.edu.cn/customer/masterpage/masterpage.html#/model/twogradepage/newsdetail?id=13&LMBH=25&t=0.48460132974326675) 的说明，下载对应系统的 VPN 工具，用自己的学号登录。
3. 然后在 [电子科技大学高性能计算中心](https://hpc.uestc.edu.cn/customer/index/index.html#/) 的主页进入高性能计算中心的系统。

### 登录节点

1. 进入系统后即进入到了登录节点。打开「应用仓库」,找到「terminal」软件并启用。
2. 打开「terminal」，使用命令 `git clone` 下载这个仓库到根目录，然后 `cd hpc-guide` 进入仓库。
3. 使用命令 `bash scripts/hpc_env_check.sh` 运行环境检测脚本，了解登录节点的环境情况。
4. 正常来讲是没有登录节点是没有配置 conda 的。使用命令 `bash scripts/install_conda.sh` 来安装 conda。
5. 上传文件或者用 git 创建你的代码项目，使用 conda 配置环境。

   **注意：**根据测试，conda 环境求解速度较慢，建议使用 conda 作为环境隔离，使用 pip 下载安装依赖项。
6. 完成后使用 `exit` 命令退出「terminal」软件。

### 计算节点

1. 在首页点击「开发中心」，进入后点击「新建开发环境」。
2. 在弹出的标签页中进行配置：
    1. 用途与镜像：
        - 环境类型：VSCode
        - 选择镜像：jhinno/webide-vscode:v6.1（这个为平台官方镜像）
        - SSH连接：按需开启
    2. 环境资源：
        - 这个页面按需选择即可
    3. 挂载目录：
        - 将 conda 的安装目录（通常为 `/data/home/202422010511/miniconda3`）和你的代码项目目录挂载上去
    4. 环境资源：
        - 这个页面根据实际情况填写，建议进行合理且规范的命名。
3. 创建好的环境可以点击「启动」，随后点击「VSCode」以进入计算节点，进入后即**开始收费**。
4. 进入后如果没有打开文件夹，点击左上角的「三条横线（≡）」按钮，选择「File」，再选择「Open Folder...」即可在 VSCode 中打开你的代码项目。
5. 使用快捷键「Ctrl+J」打开终端窗口，然后使用 `cd` 命令跳转到本文件所在目录，然后使用命令 `bash scripts/gpu_env_check.sh` 来检测环境 GPU。
6. 最后尝试在终端里面激活 conda 环境，随后即可开始训练。
7. 训练结束后，务必**手动停止**开发环境，不然会持续扣费。
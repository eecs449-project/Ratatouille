const { createApp } = Vue;

createApp({
    data() {
        return {
            appName: "Ratatouille",
            welcomeText:
                "Hi, welcome to Ratatouille! Go ahead and send me a message:)",
            chatHistory: [],
            msgerForm: null,
            msgerInput: null,
            msgerChat: null,
            BOT_IMG: "../static/images/bot_img.jpg",
            USER_IMG: "../static/images/userimg.png",
            BOT_NAME: "The Chef",
            USER_NAME: "You",
            typeIndicator: null,
            isTyping: false,
            typingTimeout: null,
            cur_num: 0,
            target_num: 5,
            disable: false
        };
    },
    methods: {
        appendMessage(name, img, side, text) {
            const msgDiv = document.createElement("div");
            msgDiv.classList.add("msg", `${side}-msg`);
            msgDiv.innerHTML = `
                    <img class="msg-img" src="${img}">
                    <div class="msg-bubble">
                        <div class="msg-info">
                            <div class="msg-info-name">${name}</div>
                            <div class="msg-info-time">${this.formatDate(
                new Date()
            )}</div>
                        </div>
                        <div class="msg-text">${text}</div>
                    </div>
                `;

            this.msgerChat.appendChild(msgDiv);


            this.scrollToBottom();
        },

        show_eval(name, img, side){
            const msgDiv = document.createElement("div");
            msgDiv.classList.add("msg", `${side}-msg`);
            msgDiv.innerHTML = `
                    <img class="msg-img" src="${img}">
                    <div class="msg-bubble">
                        <div class="msg-info">
                            <div class="msg-info-name">${name}</div>
                            <div class="msg-info-time">${this.formatDate(
                                new Date()
                            )}</div>
                        </div>
                        <div class="msg-text">
                            <p>If you think I can do better in helping you make dishes, please use the below entry to 
                                give me more recipes! To disable this feedback function in your future response, please input '/disable'.
                                (Input '/enable' to reactivate this feature)</p>
                            <form action = "/upload" method=post enctype=multipart/form-data>
                                <input type=file name=file>
                                <button  class = "btn btn-warning" type = "submit" style = "margin-left:25px" >Submit!</button>
                            </form>
                        </div>
                    </div>
                `;

            this.msgerChat.appendChild(msgDiv);


            this.scrollToBottom();
        },

        botResponse(rawText) {
            $.get("/get", { msg: rawText }).done((data) => {
                const msgText = data;
                const messageObjLeft = {
                    id: Date.now(),
                    name: this.BOT_NAME,
                    img: this.BOT_IMG,
                    side: "left",
                    text: msgText,
                };
                this.chatHistory.push(messageObjLeft);
                this.appendMessage(this.BOT_NAME, this.BOT_IMG, "left", msgText);
                sessionStorage.setItem(
                    "chatHistory",
                    JSON.stringify(this.chatHistory)
                );
                if (this.cur_num === this.target_num && !this.disable) {
                    this.show_eval(this.BOT_NAME, this.BOT_IMG, "left");
                    this.cur_num = 0;
                } 
            });
        },

        formatDate(date) {
            const h = ("0" + date.getHours()).slice(-2);
            const m = ("0" + date.getMinutes()).slice(-2);
            return `${h}:${m}`;
        },

        changeHelper() {
            this.isTyping = true;
            clearTimeout(this.typingTimeout);
            this.typingTimeout = setTimeout(() => {
                this.isTyping = false;
            }, 1000);
        },

        scrollToBottom() {
            this.$nextTick(() => {
                if (this.msgerChat) {
                    this.msgerChat.scrollTop = this.msgerChat.scrollHeight;
                }
            });
        },

        loadChatHistory() {
            const savedHistory = sessionStorage.getItem("chatHistory");
            if (savedHistory) {
                this.chatHistory = JSON.parse(savedHistory);
                console.log(this.chatHistory);
                this.chatHistory.forEach((msg) => {
                    this.appendMessage(msg.name, msg.img, msg.side, msg.text);
                })
                this.scrollToBottom();
            }
        }
    },

    mounted() {
        this.$nextTick(() => {
            this.msgerForm = document.querySelector(".msger-inputarea");
            this.msgerInput = document.querySelector(".msger-input");
            this.msgerChat = document.querySelector(".msger-chat");
            this.typeIndicator = document.getElementById("typeIndicator");

            this.msgerForm.addEventListener("submit", (event) => {
                event.preventDefault();

                const msgText = this.msgerInput.value;
                if (!msgText) return;

                this.msgerInput.value = "";
                this.appendMessage(
                    this.USER_NAME,
                    this.USER_IMG,
                    "right",
                    msgText
                );

                if (msgText === "/disable"){
                    this.appendMessage(
                        this.BOT_NAME,
                        this.BOT_IMG,
                        "left",
                        "Feedback feature has been successfully disabled!"
                    );
                    this.disable = true;
                    return;
                }
                else if (msgText === "/enable"){
                    this.appendMessage(
                        this.BOT_NAME,
                        this.BOT_IMG,
                        "left",
                        "Feedback feature has been successfully reactivated"
                    );
                    this.disable = false;
                    this.cur_num = 0;
                    return;
                }

                const messageObjRight = {
                    id: Date.now(),
                    name: this.USER_NAME,
                    img: this.USER_IMG,
                    side: "right",
                    text: msgText,
                }
                this.chatHistory.push(messageObjRight);
                //this.appendMessage(this.BOT_NAME, this.BOT_IMG, "left", "Test Message");
                this.botResponse(msgText);
                this.cur_num ++;

                sessionStorage.setItem("chatHistory", JSON.stringify(this.chatHistory));

                this.scrollToBottom();
            });

            this.scrollToBottom();
            this.loadChatHistory();
        });
    },
}).mount("#app");

const BOT_NAME = "Joe Bot";
const BORING_ANSWER = "I'm not able to understand your request. Please try again, or <a href=\"/documentation\">consult the documentation</a>.";

const DocumentationQueries = [
    { match: /add.*student|new.*student|import.*student/i, reference: "adding-students" }
]

const Author = {
    BOT: 0,
    USER: 1
}

const qnaOpenButton = $el("#help-button");
const qnaCloseButton = $el("#close-qna-button");
const qnaChat = $el("#qna-chat");
const chatMessageContainer = $el("#chat-messages");
const chatInput = $el("#chat-input");
const typingIndicator = $el("#typing-indicator");

qnaChat.addEventListener("click", function (event) {
    event.preventDefault();
    chatInput.focus();
});

qnaOpenButton.addEventListener("click", function () {
    qnaOpenButton.classList.add("hidden");
    qnaChat.classList.remove("hidden");
    chatInput.focus();
});

qnaCloseButton.addEventListener("click", function () {
    qnaOpenButton.classList.remove("hidden");
    qnaChat.classList.add("hidden");
});

chatInput.addEventListener("keydown", function (event) {
    if (event.key !== "Enter") return;

    const userPrompt = chatInput.value;

    renderMessage(Author.USER, userPrompt);
    chatInput.value = "";

    // Prevent desync and other shenanigans
    chatInput.disabled = true;

    // If we make it look like something is happening it will seem like something is happening
    setTimeout(function () {
        setTyping(true);
    }, 150);

    setTimeout(function () {
        const botMessage = getBotResponse(userPrompt);
        renderMessage(Author.BOT, botMessage);
        setTyping(false);

        chatInput.disabled = false;
        chatInput.focus();
    }, 1700);
});

function getBotResponse(message) {
    for (const query of DocumentationQueries) {
        console.log(query.match, message)
        console.log(message.match(query.match));
        if (!message.match(query.match)) continue;
        const docChunk = $el(`#docs-${query.reference}`);
        const href = `/documentation#${docChunk.id}`;
        return `${docChunk.innerHTML}<hr>See <a href="${href}">the documentation</a> for more information.`;
    }

    return BORING_ANSWER;
}

function setTyping(isTyping) {
    if (!isTyping) {
        const typingEl = $el("#typing-indicator");
        if (typingEl) typingEl.remove();
        return;
    }

    const messageWrapper = $e("div", chatMessageContainer, { classes: ["chat-message-wrapper"], id: "typing-indicator" });
    $e("div", messageWrapper, { classes: ["chat-message", "bot"], innerText: `${BOT_NAME} is thinking...` });
    messageWrapper.scrollIntoView();
}

function renderMessage(author, content) {
    // Shows a message in the chat given an author of enum type Author and content string

    let authorCSSClass = {
        [Author.BOT]: "bot",
        [Author.USER]: "user",
    }[author];

    // Author param isn't a handled enum member, throw an error.
    if (!authorCSSClass) throw new Error("Bad Author");

    const messageWrapper = $e("div", chatMessageContainer, { classes: ["chat-message-wrapper"] });

    // HACK: Ugly align hack with flexbox. Blehhhhhhhhhh!
    const alignLeft = author === Author.BOT;
    if (!alignLeft) $e("spacer", messageWrapper);

    const message = $e("div", messageWrapper, { classes: ["chat-message", authorCSSClass] });
    if (author === Author.BOT) {
        // Do not escape HTML for the bot as it needs to steal content from docs pages
        message.innerHTML = content;

        // And make documentation element references work
        hookElementDescendantsForElementReferences(message);
    } else {
        // The user, on the other hand, is one shifty freak. Escape that input NOW!!!
        message.innerText = content;
    }

    if (alignLeft) $e("spacer", messageWrapper);
    messageWrapper.scrollIntoView();
}

renderMessage(Author.BOT, "Hello, and welcome to Spirit!");
renderMessage(Author.USER, "okay");
renderMessage(Author.BOT, `I am ${BOT_NAME}, and my job is to help you navigate through using Spirit.`);
renderMessage(Author.USER, "okay");
renderMessage(Author.BOT, "Please ask any questions you may have!");
renderMessage(Author.USER, "okay");
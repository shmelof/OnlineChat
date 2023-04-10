from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import run_async, run_js

import asyncio

chat_mss = []
online_users = set()

MAX_MESSAGES_COUNT = 100


async def main():
    global chat_mss

    put_markdown('Hello! Welcome to the my online chat!\nHave a good day!')

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    nik = await input("Go Chat!", required=True, placeholder="Your Name", validate=lambda n: "This nickname use yet:(" if n in online_users or n == '/' else None)
    online_users.add(nik)

    chat_mss.append(('/', f"'{nik}'join to Chat!"))
    msg_box.append(put_markdown(f"'{nik}'join to Chat!"))

    refresh_task = run_async(refresh_msg(nik, msg_box))

    while True:
        data = await input_group("New message", [
            input(placeholder="Text", name="msg"),
            actions(name="cmd", buttons=["Send message", {'label':"Quit from chat", "type":"cancel"}])
        ], validate=lambda m: ('msg', "Text") if m["cmd"] == "Send message" and not m["msg"] else None)

        if data is None:
            break

        msg_box.append(put_markdown(f"'{nik}': {data['msg']}"))
        chat_mss.append((nik, data['msg']))

    #exit chat
    refresh_task.close()

    online_users.remove(nik)
    toast("You leave from chat")
    msg_box.append(put_markdown(f"User '{nik}' leave chat"))
    chat_mss.append(('/', f"User '{nik}' leave chat"))


async def refresh_msg(nik, msg_box):
    global chat_mss
    last_idx = len(chat_mss)

    while True:
        await asyncio.sleep(1)

        for m in chat_mss[last_idx:]:
            if m[0] != nik:
                msg_box.append(put_markdown(f"'{m[0]}':{m[1]}"))

        #remove expired
        if len(chat_mss) > MAX_MESSAGES_COUNT:
            chat_mss = chat_mss[len(chat_mss) // 2:]

        last_idx = len(chat_mss)


if __name__ == '__main__':
    start_server(main, debug=True, port=8080, cdn=False)
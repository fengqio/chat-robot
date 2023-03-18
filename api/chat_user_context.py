import json

import openai

from util.log import logger

model_engine = "gpt-3.5-turbo"
retry_times = 2


class ChatUserContext:
    def __init__(self, sender_staff_id, sender_nick, context_size) -> None:
        self.context_list = []
        self.context_size = context_size
        self.sender_staff_id = sender_staff_id
        self.sender_nick = sender_nick

    def chat(self, prompt):
        self.context_list.append({"role": "user", "content": prompt})
        length = len(self.context_list)
        messages = self.context_list[length - self.context_size:length]
        content = chatWithRetry(self.sender_nick, self.sender_staff_id, messages)
        if len(content) > 0:
            self.context_list.append({"role": "assistant", "content": content})
        return content

    def __str__(self):
        return json.dumps(
            {'user_id': self.sender_staff_id, 'user_name': self.sender_nick, 'context_list': self.context_list,
             'context_size': self.context_size})


def chatWithRetry(sender_nick, sender_staff_id, messages):
    content = ''
    logger.info(f"senderStaffId:{sender_staff_id} senderNick:{sender_nick} messages:{messages}")
    for i in range(retry_times):
        try:
            completion = openai.ChatCompletion.create(
                model=model_engine,
                messages=messages,
                max_tokens=2048
            )
            logger.info(f"token usage {json.dumps(completion.usage)}")
            content = completion.choices[0].message.content
            break
        except Exception as e:
            logger.info(f"failed retry, msg:{e.user_message}")
            continue
    logger.info(f"receive chat-gpt response: {content}")
    return content

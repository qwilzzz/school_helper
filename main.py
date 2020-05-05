from app.school_helper import Bot
from app.bot_config import vk_token, group_id

if __name__ == '__main__':
    school_helper = Bot(api_token = vk_token, group_id = group_id, logging = True)
    school_helper.mainloop()

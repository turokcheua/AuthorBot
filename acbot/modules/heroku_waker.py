
#              © Copyright 2022
#           https://t.me/authorche
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import logging
import os

try:
    import redis
except ImportError as e:
    if "DYNO" in os.environ:
        raise e

from telethon.tl.types import Message

from .. import loader, main, utils, heroku

from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest

logger = logging.getLogger(__name__)


@loader.tds
class HerokuMod(loader.Module):
    """Stuff related to AuthorBot Heroku installation"""

    strings = {
        "name": "Heroku",
        "redisdocs": (
            "<emoji document_id=5458675903028535170>🛍</emoji> <b>Redis"
            " Database</b>\n\n🇷🇺 <b>If you are from Russia, or just want to use"
            " external service:</b>\n1. Go to https://redis.com\n2. Register"
            " account\n3. Create database instance\n4. Enter your Redis Database URL"
            " via <code>.setredis &lt;redis_url&gt;</code>\n<i><emoji"
            " document_id=6318918617891080008>💡</emoji> Hint: URL structure is"
            " <code>redis://:PASSWORD@ENDPOINT</code></i>\n\n♓️ <b>If you are not from"
            " Russia, just enable </b><code>heroku-redis</code><b> plugin for your app."
            " For this action Heroku account verification is required!</b>"
        ),
        "url_invalid": (
            "<emoji document_id=5379568936218009290>👎</emoji> <b>Invalid URL"
            " specified</b>"
        ),
        "url_saved": (
            "<emoji document_id=5368324170671202286>👍</emoji> <b>URL saved</b>"
        ),
    }

    strings_ru = {
        "redisdocs": (
            "<emoji document_id=5458675903028535170>🛍</emoji> <b>База данных"
            " Redis</b>\n\n🇷🇺 <b>Если ты из России, или просто хочешь использовать"
            " внешний сервис:</b>\n1. Перейди на https://redis.com\n2."
            " Зарегистрируйся\n3. Создай базу данных\n4. Введи Database URL в"
            " <code>.setredis &lt;redis_url&gt;</code>\n<i><emoji"
            " document_id=6318918617891080008>💡</emoji> Подсказка: URL выглядит так:"
            " <code>redis://:PASSWORD@ENDPOINT</code></i>\n\n♓️ <b>Если ты не из"
            " России, можешь просто активировать плагин"
            " </b><code>heroku-redis</code><b> в Hikka app Heroku. Для этого тебе нужно"
            " будет верифицировать аккаунт</b>"
        ),
        "url_invalid": (
            "<emoji document_id=5379568936218009290>👎</emoji> <b>Указан неверный"
            " URL</b>"
        ),
        "url_saved": (
            "<emoji document_id=5368324170671202286>👍</emoji> <b>URL сохранен</b>"
        ),
    }

    _bot = "@WebpageBot"

    async def client_ready(self):
        if "DYNO" not in os.environ:
            raise loader.SelfUnload

        await utils.dnd(self._client, self._bot, True)

        self._heroku_url = heroku.get_app(api_token=main.hikka.api_token)[0].web_url
        self._heroku_pinger.start()

    @loader.command(ru_doc="<ссылка Redis> - Установить базу данных Redis")
    async def setredis(self, message: Message):
        """<redis_url> - Set Redis Database URL"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("redisdocs"))
            return

        try:
            redis.from_url(args)
        except Exception:
            await utils.answer(message, self.strings("url_invalid"))
            return

        main.save_config_key("redis_uri", args)
        await self._db.redis_init()
        await self._db.remote_force_save()
        await utils.answer(message, self.strings("url_saved"))

    @loader.loop(interval=20 * 60, wait_before=True)
    async def _heroku_pinger(self):
        """Sends request to Heroku webapp through WebpageBot"""
        async with self._client.conversation(self._bot) as conv:
            try:
                m = await conv.send_message(self._heroku_url)
            except YouBlockedUserError:
                await self._client(UnblockRequest(self._bot))
                m = await conv.send_message(self._heroku_url)

            r = await conv.get_response()
            await m.delete()
            await r.delete()

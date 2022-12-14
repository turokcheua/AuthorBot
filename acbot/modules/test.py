
#              ÂŠ Copyright 2022
#           https://t.me/authorche
#
# đ      Licensed under the GNU AGPLv3
# đ https://www.gnu.org/licenses/agpl-3.0.html

import inspect
import logging
import os
import random
import time
from io import BytesIO
import typing

from telethon.tl.functions.channels import EditAdminRequest, InviteToChannelRequest
from telethon.tl.types import ChatAdminRights, Message

from .. import loader, main, utils
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)

DEBUG_MODS_DIR = os.path.join(utils.get_base_dir(), "debug_modules")

if not os.path.isdir(DEBUG_MODS_DIR):
    os.mkdir(DEBUG_MODS_DIR, mode=0o755)

for mod in os.scandir(DEBUG_MODS_DIR):
    os.remove(mod.path)


@loader.tds
class TestMod(loader.Module):
    """Perform operations based on userbot self-testing"""

    _memory = {}

    strings = {
        "name": "Tester",
        "set_loglevel": "đĢ <b>Please specify verbosity as an integer or string</b>",
        "no_logs": "âšī¸ <b>You don't have any logs at verbosity {}.</b>",
        "logs_filename": "acbot-logs.txt",
        "logs_caption": (
            "<emoji document_id=5188377234380954537>đ</emoji> <b>AuthorChe's logs with"
            " verbosity </b><code>{}</code>\n\n<emoji"
            " document_id=5454390891466726015>đ</emoji> <b>AuthorChe's version:"
            " {}.{}.{}</b>{}\n<emoji document_id=6321050180095313397>âą</emoji>"
            " <b>Uptime: {}</b>\n<b>{}</b>\n\n<b>{} NoNick</b>\n<b>{} Grep</b>\n<b>{}"
            " InlineLogs</b>"
        ),
        "suspend_invalid_time": (
            "<emoji document_id=5416024721705673488>đ</emoji> <b>Invalid time to"
            " suspend</b>"
        ),
        "suspended": (
            "<emoji document_id=5452023368054216810>đĨļ</emoji> <b>Bot suspended"
            " for</b> <code>{}</code> <b>seconds</b>"
        ),
        "results_ping": (
            "<emoji document_id=6321050180095313397>âą</emoji> <b>AuthorChe's ping:</b>"
            " <code>{}</code> <b>ms</b>\n<emoji"
            " document_id=5377371691078916778>đ</emoji> <b>Uptime: {}</b>"
        ),
        "ping_hint": (
            "<emoji document_id=5472146462362048818>đĄ</emoji> <i>Telegram ping mostly"
            " depends on Telegram servers latency and other external factors and has"
            " nothing to do with the parameters of server on which userbot is"
            " installed</i>"
        ),
        "confidential": (
            "â ī¸ <b>Log level </b><code>{}</code><b> may reveal your confidential info,"
            " be careful</b>"
        ),
        "confidential_text": (
            "â ī¸ <b>Log level </b><code>{0}</code><b> may reveal your confidential info,"
            " be careful</b>\n<b>Type </b><code>.logs {0} force_insecure</code><b> to"
            " ignore this warning</b>"
        ),
        "choose_loglevel": "đââī¸ <b>Choose log level</b>",
        "bad_module": "đĢ <b>Module not found</b>",
        "debugging_enabled": (
            "đ§âđģ <b>Debugging mode enabled for module </b><code>{0}</code>\n<i>Go to"
            " directory named `debug_modules`, edit file named `{0}.py` and see changes"
            " in real time</i>"
        ),
        "debugging_disabled": "â <b>Debugging disabled</b>",
    }

    strings_ru = {
        "set_loglevel": "đĢ <b>ĐŖĐēĐ°ĐļĐ¸ ŅŅĐžĐ˛ĐĩĐŊŅ ĐģĐžĐŗĐžĐ˛ ŅĐ¸ŅĐģĐžĐŧ Đ¸ĐģĐ¸ ŅŅŅĐžĐēĐžĐš</b>",
        "no_logs": "âšī¸ <b>ĐŖ ŅĐĩĐąŅ ĐŊĐĩŅ ĐģĐžĐŗĐžĐ˛ ŅŅĐžĐ˛ĐŊŅ {}.</b>",
        "logs_filename": "acbot-logs.txt",
        "logs_caption": (
            "<emoji document_id=5188377234380954537>đ</emoji> <b>ĐĐžĐŗĐ¸ AuthorChe's ŅŅĐžĐ˛ĐŊŅ"
            " </b><code>{}</code>\n\n<emoji document_id=5454390891466726015>đ</emoji>"
            " <b>ĐĐĩŅŅĐ¸Ņ AuthorChe's: {}.{}.{}</b>{}\n<emoji"
            " document_id=6321050180095313397>âą</emoji> <b>Uptime:"
            " {}</b>\n<b>{}</b>\n\n<b>{} NoNick</b>\n<b>{} Grep</b>\n<b>{}"
            " InlineLogs</b>"
        ),
        "bad_module": "đĢ <b>ĐĐžĐ´ŅĐģŅ ĐŊĐĩ ĐŊĐ°ĐšĐ´ĐĩĐŊ</b>",
        "debugging_enabled": (
            "đ§âđģ <b>Đ ĐĩĐļĐ¸Đŧ ŅĐ°ĐˇŅĐ°ĐąĐžŅŅĐ¸ĐēĐ° Đ˛ĐēĐģŅŅĐĩĐŊ Đ´ĐģŅ ĐŧĐžĐ´ŅĐģŅ"
            " </b><code>{0}</code>\n<i>ĐŅĐŋŅĐ°Đ˛ĐģŅĐšŅŅ Đ˛ Đ´Đ¸ŅĐĩĐēŅĐžŅĐ¸Ņ `debug_modules`,"
            " Đ¸ĐˇĐŧĐĩĐŊŅĐš ŅĐ°ĐšĐģ `{0}.py`, Đ¸ ŅĐŧĐžŅŅĐ¸ Đ¸ĐˇĐŧĐĩĐŊĐĩĐŊĐ¸Ņ Đ˛ ŅĐĩĐļĐ¸ĐŧĐĩ ŅĐĩĐ°ĐģŅĐŊĐžĐŗĐž Đ˛ŅĐĩĐŧĐĩĐŊĐ¸</i>"
        ),
        "debugging_disabled": "â <b>Đ ĐĩĐļĐ¸Đŧ ŅĐ°ĐˇŅĐ°ĐąĐžŅŅĐ¸ĐēĐ° Đ˛ŅĐēĐģŅŅĐĩĐŊ</b>",
        "suspend_invalid_time": (
            "<emoji document_id=5416024721705673488>đ</emoji> <b>ĐĐĩĐ˛ĐĩŅĐŊĐžĐĩ Đ˛ŅĐĩĐŧŅ"
            " ĐˇĐ°ĐŧĐžŅĐžĐˇĐēĐ¸</b>"
        ),
        "suspended": (
            "<emoji document_id=5452023368054216810>đĨļ</emoji> <b>ĐĐžŅ ĐˇĐ°ĐŧĐžŅĐžĐļĐĩĐŊ ĐŊĐ°</b>"
            " <code>{}</code> <b>ŅĐĩĐēŅĐŊĐ´</b>"
        ),
        "results_ping": (
            "<emoji document_id=6321050180095313397>âą</emoji> <b>AuthorChe's ping:</b>"
            " <code>{}</code> <b>ms</b>\n<emoji"
            " document_id=5377371691078916778>đ</emoji> <b>Uptime: {}</b>"
        ),
        "ping_hint": (
            "@AuthorChe_bot ĐŋŅĐ°ŅŅŅ ŅŅĐ°ĐąŅĐģŅĐŊĐž :)"
        ),
        "confidential": (
            "â ī¸ <b>ĐŖŅĐžĐ˛ĐĩĐŊŅ ĐģĐžĐŗĐžĐ˛ </b><code>{}</code><b> ĐŧĐžĐļĐĩŅ ŅĐžĐ´ĐĩŅĐļĐ°ŅŅ ĐģĐ¸ŅĐŊŅŅ"
            " Đ¸ĐŊŅĐžŅĐŧĐ°ŅĐ¸Ņ, ĐąŅĐ´Ņ ĐžŅŅĐžŅĐžĐļĐĩĐŊ</b>"
        ),
        "confidential_text": (
            "â ī¸ <b>ĐŖŅĐžĐ˛ĐĩĐŊŅ ĐģĐžĐŗĐžĐ˛ </b><code>{0}</code><b> ĐŧĐžĐļĐĩŅ ŅĐžĐ´ĐĩŅĐļĐ°ŅŅ ĐģĐ¸ŅĐŊŅŅ"
            " Đ¸ĐŊŅĐžŅĐŧĐ°ŅĐ¸Ņ, ĐąŅĐ´Ņ ĐžŅŅĐžŅĐžĐļĐĩĐŊ</b>\n<b>ĐĐ°ĐŋĐ¸ŅĐ¸ </b><code>.logs {0}"
            " force_insecure</code><b>, ŅŅĐžĐąŅ ĐžŅĐŋŅĐ°Đ˛Đ¸ŅŅ ĐģĐžĐŗĐ¸ Đ¸ĐŗĐŊĐžŅĐ¸ŅŅŅ"
            " ĐŋŅĐĩĐ´ŅĐŋŅĐĩĐļĐ´ĐĩĐŊĐ¸Đĩ</b>"
        ),
        "choose_loglevel": "đââī¸ <b>ĐŅĐąĐĩŅĐ¸ ŅŅĐžĐ˛ĐĩĐŊŅ ĐģĐžĐŗĐžĐ˛</b>",
        "_cmd_doc_dump": "ĐĐžĐēĐ°ĐˇĐ°ŅŅ Đ¸ĐŊŅĐžŅĐŧĐ°ŅĐ¸Ņ Đž ŅĐžĐžĐąŅĐĩĐŊĐ¸Đ¸",
        "_cmd_doc_logs": (
            "<ŅŅĐžĐ˛ĐĩĐŊŅ> - ĐŅĐŋŅĐ°Đ˛ĐģŅĐĩŅ ĐģĐžĐŗ-ŅĐ°ĐšĐģ. ĐŖŅĐžĐ˛ĐŊĐ¸ ĐŊĐ¸ĐļĐĩ WARNING ĐŧĐžĐŗŅŅ ŅĐžĐ´ĐĩŅĐļĐ°ŅŅ"
            " ĐģĐ¸ŅĐŊŅŅ Đ¸ĐŊŅĐžĐŧŅĐ°ŅĐ¸Ņ."
        ),
        "_cmd_doc_suspend": "<Đ˛ŅĐĩĐŧŅ> - ĐĐ°ĐŧĐžŅĐžĐˇĐ¸ŅŅ ĐąĐžŅĐ° ĐŊĐ° ĐŊĐĩĐēĐžŅĐžŅĐžĐĩ Đ˛ŅĐĩĐŧŅ",
        "_cmd_doc_ping": "ĐŅĐžĐ˛ĐĩŅŅĐĩŅ ŅĐēĐžŅĐžŅŅŅ ĐžŅĐēĐģĐ¸ĐēĐ° ŅĐˇĐĩŅĐąĐžŅĐ°",
        "_cls_doc": "ĐĐŋĐĩŅĐ°ŅĐ¸Đ¸, ŅĐ˛ŅĐˇĐ°ĐŊĐŊŅĐĩ Ņ ŅĐ°ĐŧĐžŅĐĩŅŅĐ¸ŅĐžĐ˛Đ°ĐŊĐ¸ĐĩĐŧ",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "force_send_all",
                False,
                "â ī¸ Do not touch, if you don't know what it does!\nBy default, AuthorChe's"
                " will try to determine, which client caused logs. E.g. there is a"
                " module TestModule installed on Client1 and TestModule2 on Client2. By"
                " default, Client2 will get logs from TestModule2, and Client1 will get"
                " logs from TestModule. If this option is enabled, AuthorChe's will send all"
                " logs to Client1 and Client2, even if it is not the one that caused"
                " the log.",
                validator=loader.validators.Boolean(),
                on_change=self._pass_config_to_logger,
            ),
            loader.ConfigValue(
                "tglog_level",
                "INFO",
                "â ī¸ Do not touch, if you don't know what it does!\n"
                "Minimal loglevel for records to be sent in Telegram.",
                validator=loader.validators.Choice(
                    ["INFO", "WARNING", "ERROR", "CRITICAL"]
                ),
                on_change=self._pass_config_to_logger,
            ),
        )

    def _pass_config_to_logger(self):
        logging.getLogger().handlers[0].force_send_all = self.config["force_send_all"]
        logging.getLogger().handlers[0].tg_level = self.config["tglog_level"]

    @loader.command(ru_doc="ĐŅĐ˛ĐĩŅŅ ĐŊĐ° ŅĐžĐžĐąŅĐĩĐŊĐ¸Đĩ, ŅŅĐžĐąŅ ĐŋĐžĐēĐ°ĐˇĐ°ŅŅ ĐĩĐŗĐž Đ´Đ°ĐŧĐŋ")
    async def dump(self, message: Message):
        """Use in reply to get a dump of a message"""
        if not message.is_reply:
            return

        await utils.answer(
            message,
            "<code>"
            + utils.escape_html((await message.get_reply_message()).stringify())
            + "</code>",
        )

    @loader.loop(interval=1)
    async def watchdog(self):
        if not os.path.isdir(DEBUG_MODS_DIR):
            return

        try:
            for module in os.scandir(DEBUG_MODS_DIR):
                last_modified = os.stat(module.path).st_mtime
                cls_ = module.path.split("/")[-1].split(".py")[0]

                if cls_ not in self._memory:
                    self._memory[cls_] = last_modified
                    continue

                if self._memory[cls_] == last_modified:
                    continue

                self._memory[cls_] = last_modified
                logger.debug(f"Reloading debug module {cls_}")
                with open(module.path, "r") as f:
                    try:
                        await next(
                            module
                            for module in self.allmodules.modules
                            if module.__class__.__name__ == "LoaderMod"
                        ).load_module(
                            f.read(),
                            None,
                            save_fs=False,
                        )
                    except Exception:
                        logger.exception("Failed to reload module in watchdog")
        except Exception:
            logger.exception("Failed debugging watchdog")
            return

    @loader.command(
        ru_doc=(
            "[ĐŧĐžĐ´ŅĐģŅ] - ĐĐģŅ ŅĐ°ĐˇŅĐ°ĐąĐžŅŅĐ¸ĐēĐžĐ˛: ĐžŅĐēŅŅŅŅ ĐŧĐžĐ´ŅĐģŅ Đ˛ ŅĐĩĐļĐ¸ĐŧĐĩ Đ´ĐĩĐąĐ°ĐŗĐ° Đ¸ ĐŋŅĐ¸ĐŧĐĩĐŊŅŅŅ"
            " Đ¸ĐˇĐŧĐĩĐŊĐĩĐŊĐ¸Ņ Đ¸Đˇ ĐŊĐĩĐŗĐž Đ˛ ŅĐĩĐļĐ¸ĐŧĐĩ ŅĐĩĐ°ĐģŅĐŊĐžĐŗĐž Đ˛ŅĐĩĐŧĐĩĐŊĐ¸"
        )
    )
    async def debugmod(self, message: Message):
        """[module] - For developers: Open module for debugging
        You will be able to track changes in real-time"""
        args = utils.get_args_raw(message)
        instance = None
        for module in self.allmodules.modules:
            if (
                module.__class__.__name__.lower() == args.lower()
                or module.strings["name"].lower() == args.lower()
            ):
                if os.path.isfile(
                    os.path.join(
                        DEBUG_MODS_DIR,
                        f"{module.__class__.__name__}.py",
                    )
                ):
                    os.remove(
                        os.path.join(
                            DEBUG_MODS_DIR,
                            f"{module.__class__.__name__}.py",
                        )
                    )

                    try:
                        delattr(module, "acbot_debug")
                    except AttributeError:
                        pass

                    await utils.answer(message, self.strings("debugging_disabled"))
                    return

                module.acbot_debug = True
                instance = module
                break

        if not instance:
            await utils.answer(message, self.strings("bad_module"))
            return

        with open(
            os.path.join(
                DEBUG_MODS_DIR,
                f"{instance.__class__.__name__}.py",
            ),
            "wb",
        ) as f:
            f.write(inspect.getmodule(instance).__loader__.data)

        await utils.answer(
            message,
            self.strings("debugging_enabled").format(instance.__class__.__name__),
        )

    @loader.command(ru_doc="<ŅŅĐžĐ˛ĐĩĐŊŅ> - ĐĐžĐēĐ°ĐˇĐ°ŅŅ ĐģĐžĐŗĐ¸")
    async def logs(
        self,
        message: typing.Union[Message, InlineCall],
        force: bool = False,
        lvl: typing.Union[int, None] = None,
    ):
        """<level> - Dump logs"""
        if not isinstance(lvl, int):
            args = utils.get_args_raw(message)
            try:
                try:
                    lvl = int(args.split()[0])
                except ValueError:
                    lvl = getattr(logging, args.split()[0].upper(), None)
            except IndexError:
                lvl = None

        if not isinstance(lvl, int):
            try:
                if not self.inline.init_complete or not await self.inline.form(
                    text=self.strings("choose_loglevel"),
                    reply_markup=[
                        [
                            {
                                "text": "đ¨ Critical",
                                "callback": self.logs,
                                "args": (False, 50),
                            },
                            {
                                "text": "đĢ Error",
                                "callback": self.logs,
                                "args": (False, 40),
                            },
                        ],
                        [
                            {
                                "text": "â ī¸ Warning",
                                "callback": self.logs,
                                "args": (False, 30),
                            },
                            {
                                "text": "âšī¸ Info",
                                "callback": self.logs,
                                "args": (False, 20),
                            },
                        ],
                        [
                            {
                                "text": "đ§âđģ Debug",
                                "callback": self.logs,
                                "args": (False, 10),
                            },
                            {
                                "text": "đ All",
                                "callback": self.logs,
                                "args": (False, 0),
                            },
                        ],
                        [{"text": "đĢ Cancel", "action": "close"}],
                    ],
                    message=message,
                ):
                    raise
            except Exception:
                await utils.answer(message, self.strings("set_loglevel"))

            return

        logs = "\n\n".join(
            [
                "\n".join(
                    handler.dumps(lvl, client_id=self._client.tg_id)
                    if "client_id" in inspect.signature(handler.dumps).parameters
                    else handler.dumps(lvl)
                )
                for handler in logging.getLogger().handlers
            ]
        )

        named_lvl = (
            lvl
            if lvl not in logging._levelToName
            else logging._levelToName[lvl]  # skipcq: PYL-W0212
        )

        if (
            lvl < logging.WARNING
            and not force
            and (
                not isinstance(message, Message)
                or "force_insecure" not in message.raw_text.lower()
            )
        ):
            try:
                if not self.inline.init_complete:
                    raise

                cfg = {
                    "text": self.strings("confidential").format(named_lvl),
                    "reply_markup": [
                        {
                            "text": "đ¤ Send anyway",
                            "callback": self.logs,
                            "args": [True, lvl],
                        },
                        {"text": "đĢ Cancel", "action": "close"},
                    ],
                }
                if isinstance(message, Message):
                    if not await self.inline.form(**cfg, message=message):
                        raise
                else:
                    await message.edit(**cfg)
            except Exception:
                await utils.answer(
                    message,
                    self.strings("confidential_text").format(named_lvl),
                )

            return

        if len(logs) <= 2:
            if isinstance(message, Message):
                await utils.answer(message, self.strings("no_logs").format(named_lvl))
            else:
                await message.edit(self.strings("no_logs").format(named_lvl))
                await message.unload()

            return

        if btoken := self._db.get("acbot.inline", "bot_token", False):
            logs = logs.replace(
                btoken,
                f'{btoken.split(":")[0]}:***************************',
            )

        if acbot_token := self._db.get("HikkaDL", "token", False):
            logs = logs.replace(
                acbot_token,
                f'{acbot_token.split("_")[0]}_********************************',
            )

        if acbot_token := self._db.get("Kirito", "token", False):
            logs = logs.replace(
                acbot_token,
                f'{acbot_token.split("_")[0]}_********************************',
            )

        if os.environ.get("DATABASE_URL"):
            logs = logs.replace(
                os.environ.get("DATABASE_URL"),
                "postgre://**************************",
            )

        if os.environ.get("REDIS_URL"):
            logs = logs.replace(
                os.environ.get("REDIS_URL"),
                "postgre://**************************",
            )

        if os.environ.get("acbot_session"):
            logs = logs.replace(
                os.environ.get("acbot_session"),
                "StringSession(**************************)",
            )

        logs = BytesIO(logs.encode("utf-16"))
        logs.name = self.strings("logs_filename")

        ghash = utils.get_git_hash()

        other = (
            *main.__version__,
            " <i><a"
            f' href="https://github.com/VadymYem/AuthorBot/commit/{ghash}">({ghash[:8]})</a></i>'
            if ghash
            else "",
            utils.formatted_uptime(),
            utils.get_named_platform(),
            "â" if self._db.get(main.__name__, "no_nickname", False) else "đĢ",
            "â" if self._db.get(main.__name__, "grep", False) else "đĢ",
            "â" if self._db.get(main.__name__, "inlinelogs", False) else "đĢ",
        )

        if getattr(message, "out", True):
            await message.delete()

        if isinstance(message, Message):
            await utils.answer(
                message,
                logs,
                caption=self.strings("logs_caption").format(named_lvl, *other),
            )
        else:
            await self._client.send_file(
                message.form["chat"],
                logs,
                caption=self.strings("logs_caption").format(named_lvl, *other),
            )

    @loader.owner
    @loader.command(ru_doc="<Đ˛ŅĐĩĐŧŅ> - ĐĐ°ĐŧĐžŅĐžĐˇĐ¸ŅŅ ĐąĐžŅĐ° ĐŊĐ° N ŅĐĩĐēŅĐŊĐ´")
    async def suspend(self, message: Message):
        """<time> - Suspends the bot for N seconds"""
        try:
            time_sleep = float(utils.get_args_raw(message))
            await utils.answer(
                message,
                self.strings("suspended").format(time_sleep),
            )
            time.sleep(time_sleep)
        except ValueError:
            await utils.answer(message, self.strings("suspend_invalid_time"))

    @loader.command(ru_doc="ĐŅĐžĐ˛ĐĩŅĐ¸ŅŅ ŅĐēĐžŅĐžŅŅŅ ĐžŅĐēĐģĐ¸ĐēĐ° ĐąĐžŅĐ°")
    async def ping(self, message: Message):
        """Test your userbot ping"""
        start = time.perf_counter_ns()
        message = await utils.answer(message, "<code>đģ Nofin...</code>")

        await utils.answer(
            message,
            self.strings("results_ping").format(
                round((time.perf_counter_ns() - start) / 10**6, 3),
                utils.formatted_uptime(),
            )
            + (
                ("\n\n" + self.strings("ping_hint"))
                if random.choice([0, 0, 1]) == 1
                else ""
            ),
        )

    async def client_ready(self):
        chat, is_new = await utils.asset_channel(
            self._client,
            "logs",
            "Your logs will appear in this chat",
            silent=True,
            avatar="http://p3.itc.cn/images01/20201024/0224bba14d534ae4a56e6bd747008a4c.jpeg",
        )

        self._logchat = int(f"-100{chat.id}")

        self.watchdog.start()

        if not is_new and any(
            participant.id == self.inline.bot_id
            for participant in (await self._client.get_participants(chat, limit=3))
        ):
            logging.getLogger().handlers[0].install_tg_log(self)
            logger.debug("Bot logging installed for %s", self._logchat)
            return

        logger.debug("New logging chat created, init setup...")

        try:
            await self._client(InviteToChannelRequest(chat, [self.inline.bot_username]))
        except Exception:
            logger.warning("Unable to invite logger to chat")

        try:
            await self._client(
                EditAdminRequest(
                    channel=chat,
                    user_id=self.inline.bot_username,
                    admin_rights=ChatAdminRights(ban_users=True),
                    rank="Logger",
                )
            )
        except Exception:
            pass

        logging.getLogger().handlers[0].install_tg_log(self)
        logger.debug("Bot logging installed for %s", self._logchat)

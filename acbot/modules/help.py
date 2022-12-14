#              Ā© Copyright 2022
#           https://t.me/authorche
#
# š      Licensed under the GNU AGPLv3
# š https://www.gnu.org/licenses/agpl-3.0.html

import difflib
import inspect
import logging

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class HelpMod(loader.Module):
    """Shows help for modules and commands"""

    strings = {
        "name": "Help",
        "bad_module": "<b>š« <b>Module</b> <code>{}</code> <b>not found</b>",
        "single_mod_header": (
            "<emoji document_id=5188377234380954537>š</emoji> <b>{}</b>:"
        ),
        "single_cmd": "\nā«ļø <code>{}{}</code> {}",
        "undoc_cmd": "š¦„ No docs",
        "all_header": (
            "<emoji document_id=5188377234380954537>š</emoji> <b>{} mods available,"
            " {} hidden:</b>"
        ),
        "mod_tmpl": "\n{} <code>{}</code>",
        "first_cmd_tmpl": ": ( {}",
        "cmd_tmpl": " | {}",
        "no_mod": "š« <b>Specify module to hide</b>",
        "hidden_shown": (
            "<emoji document_id=5188377234380954537>š</emoji> <b>{} modules hidden,"
            " {} modules shown:</b>\n{}\n{}"
        ),
        "ihandler": "\nš¹ <code>{}</code> {}",
        "undoc_ihandler": "š¦„ No docs",
        "partial_load": (
            "<emoji document_id=5472105307985419058>āļø</emoji> <b>Userbot is not"
            " fully loaded, so not all modules are shown</b>"
        ),
        "not_exact": (
            "<emoji document_id=5472105307985419058>āļø</emoji> <b>No exact match"
            " occured, so the closest result is shown instead</b>"
        ),
        "core_notice": (
            "<emoji document_id=5472105307985419058>āļø</emoji> <b>This is a core"
            " module. You can't unload it nor replace</b>"
        ),
    }

    strings_ru = {
         "bad_module": "<b>š« <b>Module</b> <code>{}</code> <b>not found</b>",
        "single_mod_header": (
            "<emoji document_id=5188377234380954537>š</emoji> <b>{}</b>:"
        ),
        "single_cmd": "\nā«ļø <code>{}{}</code> {}",
        "undoc_cmd": "š¦„ No docs",
        "all_header": (
            "<emoji document_id=5188377234380954537>š</emoji> <b>{} mods available,"
            " {} hidden:</b>"
        ),
        "mod_tmpl": "\n{} <code>{}</code>",
        "first_cmd_tmpl": ": ( {}",
        "cmd_tmpl": " | {}",
        "no_mod": "š« <b>Specify module to hide</b>",
        "hidden_shown": (
            "<emoji document_id=5188377234380954537>š</emoji> <b>{} modules hidden,"
            " {} modules shown:</b>\n{}\n{}"
        ),
        "ihandler": "\nš¹ <code>{}</code> {}",
        "undoc_ihandler": "š¦„ No docs",
        "partial_load": (
            "<emoji document_id=5472105307985419058>āļø</emoji> <b>Userbot is not"
            " fully loaded, so not all modules are shown</b>"
        ),
        "not_exact": (
            "<emoji document_id=5472105307985419058>āļø</emoji> <b>No exact match"
            " occured, so the closest result is shown instead</b>"
        ),
        "core_notice": (
            "<emoji document_id=5472105307985419058>āļø</emoji> <b>This is a core"
            " module. You can't unload it nor replace</b>"
        ),
    }


    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "core_emoji",
                "āŖļø",
                lambda: "Core module bullet",
                validator=loader.validators.Emoji(length=1),
            ),
            loader.ConfigValue(
                "acbot_emoji",
                "š",
                lambda: "module bullet",
                validator=loader.validators.Emoji(length=1),
            ),
            loader.ConfigValue(
                "plain_emoji",
                "ā«ļø",
                lambda: "Plain module bullet",
                validator=loader.validators.Emoji(length=1),
            ),
            loader.ConfigValue(
                "empty_emoji",
                "š",
                lambda: "Empty modules bullet",
                validator=loader.validators.Emoji(length=1),
            ),
        )

    @loader.command(
        ru_doc=(
            "<Š¼Š¾Š“ŃŠ»Ń ŠøŠ»Šø Š¼Š¾Š“ŃŠ»Šø> - Š”ŠæŃŃŃŠ°ŃŃ Š¼Š¾Š“ŃŠ»Ń(-Šø) ŠøŠ· ŠæŠ¾Š¼Š¾ŃŠø\n*Š Š°Š·Š“ŠµŠ»ŃŠ¹ Š¼Š¾Š“ŃŠ»Šø"
            " ŠæŃŠ¾Š±ŠµŠ»Š°Š¼Šø"
        )
    )
    async def helphide(self, message: Message):
        """<module or modules> - Hide module(-s) from help
        *Split modules by spaces"""
        modules = utils.get_args(message)
        if not modules:
            await utils.answer(message, self.strings("no_mod"))
            return

        mods = [i.__class__.__name__ for i in self.allmodules.modules]

        modules = list(filter(lambda module: module in mods, modules))
        currently_hidden = self.get("hide", [])
        hidden, shown = [], []
        for module in modules:
            if module in currently_hidden:
                currently_hidden.remove(module)
                shown += [module]
            else:
                currently_hidden += [module]
                hidden += [module]

        self.set("hide", currently_hidden)

        await utils.answer(
            message,
            self.strings("hidden_shown").format(
                len(hidden),
                len(shown),
                "\n".join([f"šāšØ <i>{m}</i>" for m in hidden]),
                "\n".join([f"š <i>{m}</i>" for m in shown]),
            ),
        )

    async def modhelp(self, message: Message, args: str):
        exact = True
        module = self.lookup(args)

        if not module:
            _args = args.lower()
            _args = _args[1:] if _args.startswith(self.get_prefix()) else _args
            if _args in self.allmodules.commands:
                module = self.allmodules.commands[_args].__self__

        if not module:
            module = self.lookup(
                next(
                    (
                        reversed(
                            sorted(
                                [
                                    module.strings["name"]
                                    for module in self.allmodules.modules
                                ],
                                key=lambda x: difflib.SequenceMatcher(
                                    None,
                                    args.lower(),
                                    x,
                                ).ratio(),
                            )
                        )
                    ),
                    None,
                )
            )

            exact = False

        try:
            name = module.strings("name")
        except KeyError:
            name = getattr(module, "name", "ERROR")

        _name = (
            "{} (v{}.{}.{})".format(
                utils.escape_html(name),
                module.__version__[0],
                module.__version__[1],
                module.__version__[2],
            )
            if hasattr(module, "__version__")
            else utils.escape_html(name)
        )

        reply = self.strings("single_mod_header").format(_name)
        if module.__doc__:
            reply += "<i>\nā¹ļø " + utils.escape_html(inspect.getdoc(module)) + "\n</i>"

        commands = {
            name: func
            for name, func in module.commands.items()
            if await self.allmodules.check_security(message, func)
        }

        if hasattr(module, "inline_handlers"):
            for name, fun in module.inline_handlers.items():
                reply += self.strings("ihandler").format(
                    f"@{self.inline.bot_username} {name}",
                    (
                        utils.escape_html(inspect.getdoc(fun))
                        if fun.__doc__
                        else self.strings("undoc_ihandler")
                    ),
                )

        for name, fun in commands.items():
            reply += self.strings("single_cmd").format(
                self.get_prefix(),
                name,
                (
                    utils.escape_html(inspect.getdoc(fun))
                    if fun.__doc__
                    else self.strings("undoc_cmd")
                ),
            )

        await utils.answer(
            message,
            f"{reply}\n\n{'' if exact else self.strings('not_exact')}"
            + (
                f"\n\n{self.strings('core_notice')}"
                if module.__origin__.startswith("<core")
                else ""
            ),
        )

    @loader.unrestricted
    @loader.command(ru_doc="[Š¼Š¾Š“ŃŠ»Ń] [-f] - ŠŠ¾ŠŗŠ°Š·Š°ŃŃ ŠæŠ¾Š¼Š¾ŃŃ")
    async def help(self, message: Message):
        """[module] [-f] - Show help"""
        args = utils.get_args_raw(message)
        force = False
        if "-f" in args:
            args = args.replace(" -f", "").replace("-f", "")
            force = True

        if args:
            await self.modhelp(message, args)
            return

        count = 0
        for i in self.allmodules.modules:
            try:
                if i.commands or i.inline_handlers:
                    count += 1
            except Exception:
                pass

        hidden = self.get("hide", [])

        reply = self.strings("all_header").format(
            count,
            0
            if force
            else len(
                [
                    module
                    for module in self.allmodules.modules
                    if module.__class__.__name__ in hidden
                ]
            ),
        )
        shown_warn = False

        plain_ = []
        core_ = []
        inline_ = []
        no_commands_ = []

        for mod in self.allmodules.modules:
            if not hasattr(mod, "commands"):
                logger.debug("Module %s is not inited yet", mod.__class__.__name__)
                continue

            if mod.__class__.__name__ in self.get("hide", []) and not force:
                continue

            tmp = ""

            try:
                name = mod.strings["name"]
            except KeyError:
                name = getattr(mod, "name", "ERROR")

            inline = (
                hasattr(mod, "callback_handlers")
                and mod.callback_handlers
                or hasattr(mod, "inline_handlers")
                and mod.inline_handlers
            )

            if not inline:
                for cmd_ in mod.commands.values():
                    try:
                        inline = "await self.inline.form(" in inspect.getsource(
                            cmd_.__code__
                        )
                    except Exception:
                        pass

            core = mod.__origin__.startswith("<core")

            if core:
                emoji = self.config["core_emoji"]
            elif inline:
                emoji = self.config["acbot_emoji"]
            else:
                emoji = self.config["plain_emoji"]

            if (
                not getattr(mod, "commands", None)
                and not getattr(mod, "inline_handlers", None)
                and not getattr(mod, "callback_handlers", None)
            ):
                no_commands_ += [
                    self.strings("mod_tmpl").format(self.config["empty_emoji"], name)
                ]
                continue

            tmp += self.strings("mod_tmpl").format(emoji, name)
            first = True

            commands = [
                name
                for name, func in mod.commands.items()
                if await self.allmodules.check_security(message, func) or force
            ]

            for cmd in commands:
                if first:
                    tmp += self.strings("first_cmd_tmpl").format(cmd)
                    first = False
                else:
                    tmp += self.strings("cmd_tmpl").format(cmd)

            icommands = [
                name
                for name, func in mod.inline_handlers.items()
                if await self.inline.check_inline_security(
                    func=func,
                    user=message.sender_id,
                )
                or force
            ]

            for cmd in icommands:
                if first:
                    tmp += self.strings("first_cmd_tmpl").format(f"š¹ {cmd}")
                    first = False
                else:
                    tmp += self.strings("cmd_tmpl").format(f"š¹ {cmd}")

            if commands or icommands:
                tmp += " )"
                if core:
                    core_ += [tmp]
                elif inline:
                    inline_ += [tmp]
                else:
                    plain_ += [tmp]
            elif not shown_warn and (mod.commands or mod.inline_handlers):
                reply = (
                    "<i>You have permissions to execute only these"
                    f" commands</i>\n{reply}"
                )
                shown_warn = True

        plain_.sort(key=lambda x: x.split()[1])
        core_.sort(key=lambda x: x.split()[1])
        inline_.sort(key=lambda x: x.split()[1])
        no_commands_.sort(key=lambda x: x.split()[1])
        no_commands_ = "".join(no_commands_) if force else ""

        partial_load = (
            ""
            if self.lookup("Loader")._fully_loaded
            else f"\n\n{self.strings('partial_load')}"
        )

        await utils.answer(
            message,
            "{}\n{}{}{}{}{}".format(
                reply,
                "".join(core_),
                "".join(plain_),
                "".join(inline_),
                no_commands_,
                partial_load,
            ),
        )

#!/usr/bin/env python3

import os, datetime, simple_term_menu
from discord import Embed, Webhook, RequestsWebhookAdapter, Color
from discord.embeds import EmbedProxy, EmptyEmbed

import colorful as cf

__version__ = "1.1.1"
__author__ = "Zidaan Hayat"
__email__ = "doczidaan@gmail.com"

cf.update_palette(
    {
        "coolyellow": "#ffc15e",
        "scaryred": "#ff0000",
        "slowblue": "#2a9d8f",
        "successgreen": "#419D78",
        "clearsnow": "#fcf7f8",
        "mysteriousmagenta": "#6f3eaf",
    }
)

_clear = lambda: os.system("clear")


def clr(text: str, color: str, bold: bool = False):
    color = getattr(cf, color)

    return f"{cf.bold if bold else ''}{color}{text}{cf.reset}"


def _colored_bracket(inner_char: str, out_color: str, in_color: str):
    clr_out = getattr(cf, out_color)
    clr_inn = getattr(cf, in_color)

    return f"{clr_out}[{clr_inn}{inner_char}{clr_out}]{cf.reset}"


def _ask_q_opts(options, selector: str = "=> ", title: str = None):
    return simple_term_menu.TerminalMenu(
        options, clr(title, "coolyellow", True), menu_cursor=selector
    ).show()


def _ask_q_inp(q, can_skip: bool = False):
    ask = None

    if can_skip:
        ask = input(
            _colored_bracket("?", "slowblue", "clearsnow")
            + " "
            + clr(q + " ", "coolyellow")
            + clr("(Press enter to skip)", "cyan")
            + clr("?: ", "mysteriousmagenta", True)
        )
    else:
        ask = input(
            _colored_bracket("?", "slowblue", "clearsnow")
            + " "
            + clr(q + " ", "coolyellow")
            + clr("?: ", "mysteriousmagenta", True)
        )

    if not ask or (ask.replace(" ", "") == ""):
        return None

    return ask


def _ask_q_bool(q):
    ask = input(
        f"{_colored_bracket('?', 'slowblue', 'clearsnow')} {q} ({cf.successgreen}y[yes]{cf.reset}/{cf.scaryred}n[no]{cf.reset})?: "
    )

    if ask in ["y", "yes"]:
        return True

    elif ask in ["n", "no"]:
        return False

    else:
        return None


def _print_err(msg: str):
    fmt_err = _colored_bracket("✗", "coolyellow", "scaryred") + clr(
        f" {msg}", "scaryred", True
    )
    print(fmt_err)


def _print_scc(msg: str):
    fmt_scc = _colored_bracket("✓", "coolyellow", "successgreen") + clr(
        msg, "successgreen", True
    )
    print(fmt_scc)


class WebhookConstructor:
    def __init__(self):
        self.hook_url: str = None
        self._hook_id: int = None
        self._hook_token: str = None
        self.hook: Webhook = None

        self.avatar_url: str = None
        self.username: str = None

    def start(self):
        self.construct_hook()
        return self.hook

    def construct_hook(self):
        ask = _ask_q_inp("Webhook URL")
        valid = False

        valid_hook_domains = (
            "https://discord.com/api/webhooks",
            "https://canary.discord.com/api/webhooks",
        )

        if not ask:
            _print_err(
                "Invalid URL. Must be an extension of one of the following: "
                + ", ".join(
                    clr(hook, "successgreen", False) for hook in valid_hook_domains
                )
            )
            return None

        for valid_hook in valid_hook_domains:
            if ask.lower().startswith(valid_hook):
                valid = True
                break

        if not valid:
            _print_err(
                "Invalid URL. Must be an extension of one of the following: "
                + ", ".join(
                    clr(hook, "successgreen", True) for hook in valid_hook_domains
                )
            )
            return None

        self.hook_url = ask
        split = self.hook_url.split("/")

        if not split[-2].isdigit():
            _print_err("Invalid URL. Does not contain an ID within.")
            return None

        self._hook_token = split[-1]
        self._hook_id = split[-2]

        self.hook = Webhook.partial(
            id=self._hook_id, token=self._hook_token, adapter=RequestsWebhookAdapter()
        )


class EmbedConstructor:
    def __init__(self):
        self._embed: Embed = Embed()

    def _add_attr(self, attr):
        attr = str(attr).lower()

        if attr == "timestamp":
            ask = _ask_q_bool("Set timestamp")

            if ask:
                setattr(self._embed, attr, datetime.datetime.now())
                return True

            return False

        elif attr == "color":
            r = _ask_q_inp("Color (r)")
            g = _ask_q_inp("Color (g)")
            b = _ask_q_inp("Color (b)")

            for c in (r, g, b):
                if not c.isalnum():
                    _print_err(f"{c} isn't a number")
                    return False

                if int(c) not in range(0, 256):
                    _print_err(f"{c} is not a number between 0 and 255")
                    return False

            r = int(r)
            g = int(g)
            b = int(b)

            setattr(self._embed, attr, Color.from_rgb(r, g, b))

        else:

            ask = _ask_q_inp(f"Embed {attr}")

            if ask:

                setattr(self._embed, attr, ask)
                return True

            return False

    def _add_field(self):
        name = _ask_q_inp("Name")
        value = _ask_q_inp("Value")
        inline = _ask_q_bool("Inline")

        if not inline:
            inline = False

        if not name or not value:
            _print_err("Name and Value are required")
            return False

        self._embed.add_field(name=name, value=value, inline=inline)
        return True

    def _add_author(self):
        name = _ask_q_inp("Name")

        if not name:
            _print_err("Name is required")
            return False

        url = _ask_q_inp("Author URL", True)
        icon_url = _ask_q_inp("Author Icon URL", True)

        if (url and icon_url) and not (
            url.startswith("https://") and icon_url.startswith("https://")
        ):
            _print_err("Url and Icon URL must be valid URLs")
            return False

        if not url:
            url = EmptyEmbed

        if not icon_url:
            icon_url = EmptyEmbed

        self._embed.set_author(name=name, url=url, icon_url=icon_url)
        return True

    def _add_thumbnail(self):
        thumb_url = _ask_q_inp("URL")

        if not thumb_url:
            _print_err("URL is required")
            return False

        if thumb_url and not thumb_url.startswith("https://"):
            _print_err("Thumb URL must be a valid URL")
            return False

        self._embed.set_thumbnail(url=thumb_url)
        return True

    def _add_image(self):
        img_url = _ask_q_inp("URL")

        if not img_url:
            _print_err("Image URL is required")
            return False

        if img_url and not img_url.startswith("https://"):
            _print_err("Image URL must be a valid URL")
            return False

        self._embed.set_image(url=img_url)
        return True

    def _add_footer(self):
        text = _ask_q_inp("Text")

        if not text:
            _print_err("Text is required")
            return False

        icon_url = _ask_q_inp("Footer Icon URL", True)

        if not icon_url:
            icon_url = EmptyEmbed

        self._embed.set_footer(text=text, icon_url=icon_url)

        return True

    def _show_emb(self):
        show_attrs = (
            "title",
            "description",
            "color",
            "url",
            "timestamp",
            "fields",
            "footer",
            "author",
            "thumbnail",
            "image",
        )

        m = clr("\n[ EMBED ]", "coolyellow", True)

        for attr in show_attrs:
            m += "\n" + clr(
                (attr[0].upper() + "".join(attr[1:])) + ": " + attr.upper(),
                "white",
                True,
            )

        for attr in show_attrs:
            val = getattr(self._embed, attr, None)

            if not val:
                m = m.replace(attr.upper(), clr("Not set", "coolyellow"))

            elif isinstance(val, (list, tuple, set)):
                m = m.replace(attr.upper(), clr(str(len(val)), "successgreen"))

            elif isinstance(val, EmbedProxy):
                newline = "\n"
                m = m.replace(
                    attr.upper(),
                    newline
                    + str(
                        newline.join(
                            [
                                clr(f"\t{k} -> {v}", "successgreen")
                                for k, v in list(val.__dict__.items())
                            ]
                        )
                    ),
                )

            else:
                m = m.replace(attr.upper(), clr(str(val), "successgreen"))

        print(m + '\n')

    def start(self):
        opts = {
            "Title": self._add_attr,
            "Description": self._add_attr,
            "Color": self._add_attr,
            "URL": self._add_attr,
            "Timestamp": self._add_attr,
            "Set Thumbnail": self._add_thumbnail,
            "Set Image": self._add_image,
            "Add Author": self._add_author,
            "Add Footer": self._add_footer,
            "Add Field": self._add_field,
            "Cancel": None,
            "Complete": None,
        }

        while True:
            _clear()
            self._show_emb()
            run = _ask_q_opts(opts, title="Options")

            if list(opts)[run] == list(opts)[-1]:
                break
            elif list(opts)[run].lower() in ["cancel", "exit"]:
                return False
            else:
                func = opts[list(opts)[run]]

                try:
                    func(list(opts)[run])
                except:
                    func()

        return self._embed


class ContentConstructor:
    def start(self):
        ask = _ask_q_inp(clr("Message content", "coolyellow"))

        if ask.replace(" ", "") != "":
            return ask

        return None


class Main:
    def __init__(self):
        self.content = None
        self.hook = None
        self.embeds = []

    def _ctnt(self):
        run = ContentConstructor().start()

        if run:
            self.content = run
            _print_scc("Content added!")

        return True

    def _embd(self):
        run = EmbedConstructor().start()

        if run:
            _clear()
            self.embeds.append(run)
            _print_scc("Embed added!")

        return True

    def _snd(self):
        if not (self.content or self.embeds):
            _print_err("Content or at least one embed is required")
            return None

        data = {
            "content": self.content,
        }

        if len(self.embeds) == 1:
            data["embed"] = self.embeds[0]
        else:
            data["embeds"] = self.embeds

        data["username"] = _ask_q_inp("Webhook username", True)
        data["avatar_url"] = _ask_q_inp("Webhook avatar", True)

        self.hook.send(**data)
        _print_scc("Webhook sent")

    def _cncl(self) -> None:
        return None

    def main(self):
        hook = WebhookConstructor().start()

        if not hook:
            _print_err("Cancelled, no webhook.")
            return

        self.hook = hook

        main_opts = {
            "Add Message Content": self._ctnt,
            "Add Message Embed": self._embd,
            "Send Message": self._snd,
            "Cancel Hook": self._cncl,
        }

        while True:
            _clear()
            run = _ask_q_opts(main_opts, title="Webhook Options")

            call_func = main_opts[list(main_opts)[run]]()

            if not call_func:
                break

            if "send" in list(main_opts)[run].lower():
                break

def _print_title():
    title = r'''
 __     __     ______     ______     __  __     ______     ______     __  __     ______     _______
/\ \  _ \ \   /\  ___\   /\  == \   /\ \_\ \   /\  __ \   /\  __ \   /\ \/ /    /\  == \   |==   []|
\ \ \/ ".\ \  \ \  __\   \ \  __<   \ \  __ \  \ \ \/\ \  \ \ \/\ \  \ \  _"-.  \ \  __<   |  ==== |
 \ \__/".~\_\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_____\  \ \_\ \_\  \ \_\ \_\ '-------' 
  \/_/   \/_/   \/_____/   \/_____/   \/_/\/_/   \/_____/   \/_____/   \/_/\/_/   \/_/ /_/                                                                                

'''
    print(clr(title, 'coolyellow', True))

if __name__ == "__main__":
    _clear()
    try:
        _print_title()
        Main().main()
    except KeyboardInterrupt:
        _clear()
        _print_err("Closing.")

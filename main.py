import flet as ft
import requests, base64, time, os

def main(page: ft.Page):
    page.title = "Insta Pro"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    cs = page.client_storage

    # உங்கள் நேரடி Firebase ஆன்லைன் சர்வர் இணைப்பு
    FB_URL = "https://instapro-live-89053-default-rtdb.firebaseio.com"

    SONGS = {
        "No Music": "",
        "Melody 🎵": "https://soundhelix.com",
        "Chill 🎧": "https://soundhelix.com"
    }
    REELS = [
        {"id": 1, "cat": "Nature", "u": "@nature", "t": "மலைகளின் அழகு 🏔️", "url": "https://googleapis.com", "lk": 140},
        {"id": 2, "cat": "Nature", "u": "@earth", "t": "காடுகளின் அமைதி 🌲", "url": "https://googleapis.com", "lk": 210},
        {"id": 3, "cat": "Fun", "u": "@fun_zone", "t": "சிரிப்பு நேரம் 😂", "url": "https://googleapis.com", "lk": 320}
    ]
    GRP = "👥 Global Friends Group"

    if not cs.contains_key("accs"):
        def_id = f"user_{int(time.time()) % 9999}"
        cs.set("accs", {def_id: {"uname": def_id, "nick": "Insta Pro User 😎", "bio": "Live Online! 🚀", "dp": "", "flw": 10, "flg": 5}})
        cs.set("act", def_id)
    if not cs.contains_key("blk"): cs.set("blk", [])

    def get_p():
        accs, act = cs.get("accs"), cs.get("act")
        if act not in accs:
            act = list(accs.keys())
            cs.set("act", act)
        return accs[act]

    def save_p(u):
        accs, old = cs.get("accs"), cs.get("act")
        nu = u["uname"].strip().replace(" ", "_")
        if old != nu and old in accs: del accs[old]
        accs[nu] = u; cs.set("accs", accs); cs.set("act", nu)

    # Firebase Cloud Functions
    def fb_get(p):
        try:
            r = requests.get(f"{FB_URL}/{p}.json", timeout=6)
            return r.json() if r.status_code == 200 else None
        except: return None

    def fb_post(p, d):
        try: requests.post(f"{FB_URL}/{p}.json", json=d, timeout=6)
        except: pass

    def fb_put(p, d):
        try: requests.put(f"{FB_URL}/{p}.json", json=d, timeout=6)
        except: pass

    def img_to_b64(path):
        try:
            if path and os.path.exists(path):
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
        except: pass
        return ""

    sel = {"p": ""}; plbl = ft.Text("படம் இல்லை", size=12)
    fp = ft.FilePicker(on_result=lambda e: (sel.update({"p": e.files.path}), setattr(plbl, "value", e.files.name), page.update()) if e.files else None)
    page.overlay.append(fp)
    aud = ft.Audio(src=SONGS["Melody 🎵"], autoplay=False)
    page.overlay.append(aud)

    def avt(dp, b64, nm, r=20):
        if b64: return ft.CircleAvatar(content=ft.Image(src_base64=b64, fit=ft.ImageFit.COVER, width=r*2, height=r*2), radius=r)
        if dp and dp.startswith("http"): return ft.CircleAvatar(foreground_image_src=dp, radius=r)
        return ft.CircleAvatar(content=ft.Text((nm[:2] if nm else "IP").upper()), radius=r, bgcolor=ft.Colors.PINK_100)

    body = ft.Container(expand=True); cr = {"i": 0}
    def dlg(t, c, act=None):
        d = ft.AlertDialog(title=ft.Text(t), content=c, actions=act or [ft.TextButton("மூடு", on_click=lambda e: cls(d))])
        page.dialog = d; d.open = True; page.update()
        return d
    def cls(d): d.open = False; page.update()

    # --- Multi-Account Switcher ---
    def switch_acc():
        accs, act = cs.get("accs"), cs.get("act")
        def sw(k): cs.set("act", k); cls(d); top_u.text = f"@{k} ▼"; body.content = prof_v(); page.update()
        def add_f(e):
            cls(d); un, nk, bi = ft.TextField(label="Username"), ft.TextField(label="Nickname"), ft.TextField(label="Bio")
            def cr_a(ev):
                v = un.value.strip().replace(" ", "_")
                if v:
                    a = cs.get("accs")
                    a[v] = {"uname": v, "nick": nk.value or v, "bio": bi.value, "dp": "", "flw": 10, "flg": 5}
                    cs.set("accs", a); cs.set("act", v); cls(d2); top_u.text = f"@{v} ▼"; body.content = prof_v(); page.update()
            d2 = dlg("➕ புதிய ஐடி", ft.Column([un, nk, bi], tight=True), [ft.ElevatedButton("சேர்", on_click=cr_a)])
        lst = [ft.ListTile(leading=avt("", v.get("dp", ""), k, 18), title=ft.Text(f"@{k}"), trailing=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN) if k == act else ft.Text("Switch"), on_click=lambda e, uk=k: sw(uk)) for k, v in accs.items()]
        lst.append(ft.ElevatedButton("➕ மற்றொரு ஐடி சேர்", on_click=add_f))
        d = dlg("Switch Account", ft.Column(lst, tight=True))

    # --- 1. ஆன்லைன் ஹோம் பக்கம் (Live Stories + 24h Notes + Live Feed) ---
    def home_v():
        u, blk = get_p(), cs.get("blk") or []
        me = u["uname"]

        # ஆன்லைன் ஸ்டோரிகள்
        st_data = fb_get("stories") or {}
        sr = ft.Row(scroll=ft.ScrollMode.HIDDEN, spacing=12)
        for uid, s in st_data.items():
            if uid not in blk and (time.time() - s.get("time", 0) < 86400):
                sr.controls.append(ft.GestureDetector(
                    on_click=lambda e, x=s, un=uid: play_st(un, x),
                    content=ft.Column([
                        ft.Container(content=avt("", s.get("b64", ""), un, 25), padding=2, border=ft.border.all(2, ft.Colors.PINK), border_radius=35),
                        ft.Text(un[:10], size=11)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3)
                ))

        # ஆன்லைன் 24h நோட்ஸ் (Mute Users வசதியுடன்)
        nt_data = fb_get("notes") or {}
        n_items = []
        for uid, nd in nt_data.items():
            if uid not in blk and (time.time() - nd.get("time", 0) < 86400):
                if me not in nd.get("hide", []):
                    n_items.append(ft.Container(content=ft.Text(f"💭 {uid}: {nd.get('txt', '')}", size=12), bgcolor=ft.Colors.PURPLE_50, padding=6, border_radius=8))

        ctrl_bar = ft.Row([
            ft.ElevatedButton("+ Story 🎵", on_click=lambda e: add_st()),
            ft.ElevatedButton("+ 24h Note 📝", on_click=lambda e: ed_note()),
            ft.IconButton(ft.Icons.REFRESH, on_click=lambda e: (setattr(body, "content", home_v()), page.update()))
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND)

        # ஆன்லைன் போஸ்ட்கள்
        ps_data = fb_get("posts") or {}
        fd = ft.Column(spacing=15)
        if not ps_data:
            fd.controls.append(ft.Container(content=ft.Text("இன்னும் போஸ்ட்கள் இல்லை. மேலே '+' அழுத்தி பதிவிடுங்கள்!", text_align=ft.TextAlign.CENTER), padding=25))
        else:
            for pid, p in reversed(list(ps_data.items())):
                if p.get("uname") not in blk:
                    fd.controls.append(p_card(pid, p))

        return ft.Column([ft.Container(content=sr, padding=8), ctrl_bar, ft.Row(n_items, scroll=ft.ScrollMode.HIDDEN), ft.Divider(height=10), fd], scroll=ft.ScrollMode.AUTO)

    def play_st(un, s):
        if s.get("url"): aud.src, aud.autoplay = s["url"], True; aud.update()
        img_w = ft.Image(src_base64=s["b64"], width=270, height=290, fit=ft.ImageFit.COVER) if s.get("b64") else ft.Image(src="https://picsum.photos", width=270, height=290)
        d = dlg(f"{un} • 🎵 {s.get('song', '')}", img_w, [ft.ElevatedButton("மூடு", on_click=lambda e: (aud.pause(), cls(d)))])

    def add_st():
        sel["p"], plbl.value = "", "படம் இல்லை"
        dd = ft.Dropdown(label="பாடல்", options=[ft.dropdown.Option(k) for k in SONGS], value="Melody 🎵")
        def sv(e):
            b64 = img_to_b64(sel["p"])
            fb_put(f"stories/{get_p()['uname']}", {"b64": b64, "song": dd.value, "url": SONGS[dd.value], "time": time.time()})
            cls(d); body.content = home_v(); page.update()
        d = dlg("புதிய ஆன்லைன் ஸ்டோரி", ft.Column([ft.ElevatedButton("கேலரி போட்டோ", on_click=lambda _: fp.pick_files(file_type=ft.FilePickerFileType.IMAGE)), plbl, dd], tight=True), [ft.ElevatedButton("பதிவிடு 🌍", on_click=sv)])

    def p_card(pid, p):
        lks = p.get("likes", 0); ll = ft.Text(f"{lks} likes", weight=ft.FontWeight.BOLD, size=13)
        un, cap, b64 = p.get("uname", "u"), p.get("cap", ""), p.get("b64", "")
        def lk(e):
            nl = lks + 1; fb_put(f"posts/{pid}/likes", nl); lb.icon, lb.icon_color, ll.value = ft.Icons.FAVORITE, ft.Colors.RED, f"{nl} likes"; page.update()
        def bk(e):
            b = cs.get("blk") or []
            if un not in b and un != get_p()["uname"]: b.append(un); cs.set("blk", b); body.content = home_v(); page.update()
        lb = ft.IconButton(ft.Icons.FAVORITE_BORDER, on_click=lk)
        med = ft.Image(src_base64=b64, width=400, height=260, fit=ft.ImageFit.COVER) if b64 else ft.Container(content=ft.Text(cap, size=18, color=ft.Colors.WHITE), width=400, height=180, bgcolor=ft.Colors.PINK_400, alignment=ft.alignment.center)
        return ft.Container(content=ft.Column([ft.Row([ft.Row([avt("", "", un, 16), ft.Text(un, weight=ft.FontWeight.BOLD)]), ft.PopupMenuButton(items=[ft.PopupMenuItem(text="🚫 Block", on_click=bk)])], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), med, ft.Row([lb, ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE)]), ll, ft.Text(f"{un}: {cap}", size=13)], spacing=4), padding=10, bgcolor=ft.Colors.WHITE)

    # --- 2. தொடர்புடைய ரீல்ஸ் & நேரடி ஷேர் ---
    def share_reel(r):
        def snd_r(t):
            fb_post(f"chats/{t}", {"s": get_p()["uname"], "t": f"🎬 Reel: {r['t']}", "rid": r["id"], "ru": r["u"], "rt": r["t"], "time": time.time()})
            cls(d); page.snack_bar = ft.SnackBar(ft.Text("✅ ஆன்லைன் சாட்டிற்கு அனுப்பப்பட்டது!"), open=True); page.update()
        to_in = ft.TextField(label="நண்பரின் Username (அல்லது group)", value="group")

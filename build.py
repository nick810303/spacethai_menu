#!/usr/bin/env python3
"""小泰空 richmenu → 網頁版產生器
用法: python3 build.py richmenu_project_XXXX.json
輸出: images/pageN.jpg + index.html
"""
import json, base64, sys, html
from urllib.parse import quote
from pathlib import Path

OA_ID = "@270vnkfr"          # 小泰空 LINE OA basic ID
IMG_W, IMG_H = 2500, 1686    # richmenu 標準尺寸

src = Path(sys.argv[1] if len(sys.argv) > 1 else "richmenu_project.json")
d = json.loads(src.read_text())
out = Path(__file__).parent
# 圖片放 repo 根目錄（GitHub 網頁上傳不支援子資料夾，扁平結構部署最穩）

pages_html = []
for i, p in enumerate(d["pages"]):
    n = i + 1
    b64 = p["backgroundImage"].split(",", 1)[1]
    (out / f"page{n}.jpg").write_bytes(base64.b64decode(b64))

    spots = []
    for a in p["areas"]:
        b, act = a["bounds"], a["action"]
        style = (f'left:{b["x"]/IMG_W*100:.3f}%;top:{b["y"]/IMG_H*100:.3f}%;'
                 f'width:{b["width"]/IMG_W*100:.3f}%;height:{b["height"]/IMG_H*100:.3f}%')
        t = act["type"]
        if t == "richmenuswitch":
            tgt = act["richMenuAliasId"].replace("page", "")
            spots.append(f'<a class="spot" style="{style}" href="#p{tgt}" '
                         f'onclick="show({tgt});return false" aria-label="切換頁面"></a>')
        elif t == "uri":
            uri = html.escape(act["uri"])
            spots.append(f'<a class="spot" style="{style}" href="{uri}" '
                         f'target="_blank" rel="noopener"></a>')
        elif t == "message":
            url = f'https://line.me/R/oaMessage/{quote(OA_ID)}/?{quote(act["text"])}'
            label = html.escape(act["text"])
            spots.append(f'<a class="spot" style="{style}" href="{url}" '
                         f'data-msg="{label}" title="{label}"></a>')
    pages_html.append(
        f'<div class="page" id="p{n}">'
        f'<img src="page{n}.jpg" alt="{html.escape(p["name"])}">'
        + "".join(spots) + "</div>")

page_names = [p["name"] for p in d["pages"]]
doc = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>小泰空泰式養生空間｜選單</title>
<meta property="og:title" content="小泰空泰式養生空間｜選單">
<meta property="og:image" content="page1.jpg">
<style>
  html,body{{margin:0;padding:0;background:#8f5d4e;min-height:100%}}
  .wrap{{max-width:1000px;margin:0 auto}}
  .page{{position:relative;display:none;line-height:0}}
  .page.on{{display:block}}
  .page img{{width:100%;height:auto}}
  .spot{{position:absolute;display:block;border-radius:12px;cursor:pointer}}
  .spot:hover{{background:rgba(255,255,255,.18);box-shadow:inset 0 0 0 2px rgba(255,255,255,.55)}}
  #toast{{position:fixed;left:50%;bottom:8%;transform:translateX(-50%);background:#4a2e24;color:#f5e9d9;
    padding:16px 22px;border-radius:16px;font:15px/1.6 system-ui,sans-serif;box-shadow:0 6px 24px rgba(0,0,0,.35);
    display:none;z-index:9;max-width:86%;text-align:center}}
  #toast.on{{display:block}}
  #toast b{{color:#ffb26b}}
  #toast a{{display:inline-block;margin-top:8px;background:#e07b39;color:#fff;text-decoration:none;
    padding:6px 18px;border-radius:10px;font-weight:700}}
</style>
</head>
<body>
<div class="wrap">
{chr(10).join(pages_html)}
</div>
<div id="toast"></div>
<script>
function show(n){{
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('on'));
  document.getElementById('p'+n).classList.add('on');
  history.replaceState(null,'','#p'+n);
  window.scrollTo(0,0);
}}
show(/^#p[1-5]$/.test(location.hash)?+location.hash.slice(2):1);

// 裝置分流：平板/手機（觸控）→ 提示後前往 LINE（訊息已預填，須按送出）
//          電腦 → 複製文字 + 提示貼到聊天室
var touch=/Android|iPhone|iPad/.test(navigator.userAgent)
  ||(navigator.maxTouchPoints>1&&/Mac/.test(navigator.userAgent));
var toast=document.getElementById('toast'),timer;
document.querySelectorAll('a[data-msg]').forEach(function(a){{
  a.addEventListener('click',function(e){{
    e.preventDefault();
    var t=a.dataset.msg,en=/^[\\x00-\\x7F]*$/.test(t);
    if(touch){{
      toast.innerHTML=(en
        ?'We\\u2019ll open LINE with the message pre-filled.<br>Just tap <b>Send</b> in the chat!'
        :'即將開啟 LINE，訊息已幫您填好<br>進入聊天室後請記得按<b>送出</b>！')
        +'<br><a href="'+a.href+'">'+(en?'Go to LINE':'前往 LINE')+'</a>';
    }}else{{
      navigator.clipboard&&navigator.clipboard.writeText(t);
      toast.innerHTML=(en
        ?'Copied <b>'+t+'</b>!<br>Paste &amp; send it in our LINE chat.'
        :'已複製 <b>'+t+'</b>！<br>請開啟 LINE 電腦版，貼到「小泰空」聊天室送出')
        +'<br><a href="https://line.me/R/ti/p/{quote(OA_ID)}" target="_blank" rel="noopener">'
        +(en?'Open LINE':'開啟 LINE')+'</a>';
    }}
    toast.classList.add('on');
    clearTimeout(timer);timer=setTimeout(function(){{toast.classList.remove('on')}},10000);
  }});
}});
</script>
</body>
</html>
"""
(out / "index.html").write_text(doc)
print("pages:", ", ".join(page_names))
print("written: index.html +", len(d["pages"]), "images")

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
  #toast a{{display:inline-block;margin-top:10px;background:#e07b39;color:#fff;text-decoration:none;
    padding:6px 18px;border-radius:10px;font-weight:700}}
  /* 模擬 LINE 對話框輸入列 */
  .cb{{display:flex;gap:8px;align-items:center;background:#fff;border-radius:12px;
    padding:8px 10px;margin:8px 0 0;max-width:320px}}
  .ci{{flex:1;background:#f0f1f3;border-radius:18px;padding:8px 14px;color:#333;text-align:left;
    font-size:14px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}}
  .cs{{background:#06c755;color:#fff;border-radius:10px;padding:8px 16px;font-weight:700;flex:none}}
  .ch{{font-size:12px;color:#d8b894;margin-top:4px}}
  /* 步驟式排版 */
  .tt{{font-weight:700;font-size:16px;margin-bottom:4px}}
  .tt .ok{{color:#7ee2a0;margin-right:4px}}
  .step{{display:flex;align-items:flex-start;gap:10px;text-align:left;margin-top:12px}}
  .sn{{flex:none;width:22px;height:22px;border-radius:50%;background:#e07b39;color:#fff;font-weight:700;
    font-size:13px;display:flex;align-items:center;justify-content:center;margin-top:2px}}
  .sc{{flex:1;min-width:0}}
  .sc a{{margin-top:6px}}
  .cd b{{color:#ffd76b;font-size:17px}}
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

// 裝置分流：平板/手機（觸控）→ 倒數後前往 LINE 官方帳號（訊息已預填，須按傳送）
//          電腦 → 複製文字 + 兩步驟指引（開啟 App、貼上傳送）
var touch=/Android|iPhone|iPad/.test(navigator.userAgent)
  ||(navigator.maxTouchPoints>1&&/Mac/.test(navigator.userAgent));
var toast=document.getElementById('toast'),timer,cdt;
function mock(t,en){{  // 模擬 LINE 對話框輸入列
  return '<div class="cb"><span class="ci">'+t+'</span><span class="cs">'
    +(en?'Send':'傳送')+'</span></div><div class="ch">'
    +(en?'Press <b>Enter</b> or tap <b>Send</b>':'需手動按 <b>Enter</b> 或「<b>傳送</b>」鈕')+'</div>';
}}
function step(n,inner){{return '<div class="step"><span class="sn">'+n+'</span><div class="sc">'+inner+'</div></div>';}}
document.querySelectorAll('a[data-msg]').forEach(function(a){{
  a.addEventListener('click',function(e){{
    e.preventDefault();
    clearTimeout(timer);clearInterval(cdt);
    var t=a.dataset.msg,en=/^[\\x00-\\x7F]*$/.test(t);
    if(touch){{
      toast.innerHTML='<div class="tt"><span class="ok">\\u2713</span>'
        +(en?'Message ready!':'訊息已幫您填好！')+'</div>'
        +step(1,(en
          ?'Opening our official LINE account in <b id="cdn">5</b>s\\u2026<br><a href="'+a.href+'">Go now</a>'
          :'<b id="cdn">5</b> 秒後自動前往「小泰空」LINE 官方帳號<br><a href="'+a.href+'">立即前往</a>'))
        +step(2,(en?'Send the pre-filled message':'傳送預填好的訊息')+mock(t,en));
      var n=5;
      cdt=setInterval(function(){{
        n--;var el=document.getElementById('cdn');
        if(el)el.textContent=n;
        if(n<=0){{clearInterval(cdt);location.href=a.href;}}
      }},1000);
    }}else{{
      navigator.clipboard&&navigator.clipboard.writeText(t);
      toast.innerHTML='<div class="tt"><span class="ok">\\u2713</span>'
        +(en?'Copied <b>'+t+'</b>':'已複製 <b>'+t+'</b>')+'</div>'
        +step(1,(en
          ?'Open LINE on this computer<br><a href="line://ti/p/{quote(OA_ID)}">Open LINE App</a><div class="ch">(If nothing happens, open LINE manually)</div>'
          :'開啟 LINE 電腦版<br><a href="line://ti/p/{quote(OA_ID)}">開啟 LINE App</a><div class="ch">（若按鈕沒反應，請手動開啟 LINE）</div>'))
        +step(2,(en
          ?'<b>Paste</b> in our official LINE account'
          :'到「小泰空」LINE 官方帳號<b>貼上</b>')+mock(t,en));
      timer=setTimeout(function(){{toast.classList.remove('on')}},20000);
    }}
    toast.classList.add('on');
  }});
}});
</script>
</body>
</html>
"""
(out / "index.html").write_text(doc)
print("pages:", ", ".join(page_names))
print("written: index.html +", len(d["pages"]), "images")

"""Explicit approved desktop message helper; verify target and exact output."""
import subprocess,sys,json,hashlib,datetime
from pathlib import Path
chat, filename=sys.argv[1:]
p=Path(filename); text=p.read_text()
def ax(script):
 r=subprocess.run(['osascript','-e',script],capture_output=True,text=True,check=True)
 return r.stdout
# Inspect only target composer; do not select a destination programmatically.
script='''tell application "System Events"
 tell process "WeChat"
  set es to entire contents of window 1
  repeat with e in es
   try
    if role of e is "AXTextArea" and name of e is "CHATNAME" then
     return (value of e as text)
    end if
   end try
  end repeat
  error "Target chat composer not found"
 end tell
end tell'''.replace('CHATNAME',chat)
current=ax(script).strip()
if current != text.strip():
 assert not current, 'Existing composer draft; refusing overwrite'
 subprocess.run(['pbcopy'],input=text,text=True,check=True)
 ax('tell application "System Events" to set frontmost of process "WeChat" to true')
 subprocess.run(['/opt/homebrew/bin/cliclick','w:500','c:700,600'],check=True)
 ax('tell application "System Events" to keystroke "v" using command down')
 subprocess.run(['/opt/homebrew/bin/cliclick','w:500'],check=True)
 assert ax(script).strip()==text.strip(), 'Paste differs; not sent'
# Recorded current UI Send button position; click only after target verification.
subprocess.run(['/opt/homebrew/bin/cliclick','c:1080,670','w:1000'],check=True)
assert not ax(script).strip(), 'Composer not cleared; inspect before retry'
check='''tell application "System Events"
 tell process "WeChat"
  set es to entire contents of window 1
  repeat with e in es
   try
    if role of e is "AXList" and name of e is "Messages" then
     repeat with t in static texts of e
      if (title of t as text) starts with "PREFIX" then return title of t as text
     end repeat
    end if
   end try
  end repeat
 end tell
end tell'''.replace('PREFIX',text[:40].replace('"','\\"'))
visible=ax(check)
assert visible.strip()==text.strip(), 'Outgoing text not found; inspect before retry'
(p.parent/(p.stem+'-ui-text.txt')).write_text(visible)
subprocess.run(['screencapture','-x','-R','558,52,573,650',str(p.parent/(p.stem+'-outgoing.png'))],check=True)
record={'chat':chat,'classification':'sent-ui-observed','observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'message_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'text_matches':True,'composer_empty':True,'recipient_read':None,'platform_receipt':None}
(p.parent/(p.stem+'-delivery.json')).write_text(json.dumps(record,indent=2))
print(json.dumps(record))

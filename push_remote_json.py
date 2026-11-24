# -*- coding: utf-8 -*-
"""把远端数据文件推到 veg-price-data 仓库（GitHub Pages 数据源）

只推小程序实际拉取的两个文件：prov_data.json、extra_data.json
（province_retail.json 已无消费方，停止推送，历史文件保留不动）。

用 Git Trees API 把多文件合成 **一个 commit**，避免：
  1) 逐文件 PUT 时一天产生 3 个 commit；
  2) 中途失败留下「一半新、一半旧」的半更新状态。

用法：python push_remote_json.py [--dry-run]
凭据：环境变量 GITHUB_VEG_TOKEN 优先，其次同目录 .github_token
权限：Fine-grained token 只需 veg-price-data 仓库 Contents 读写
"""
import os, sys, json, base64, ssl, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(HERE, '.github_token')
OWNER, REPO, BRANCH = 'yuluohonghuang', 'veg-price-data', 'main'
API_ROOT = 'https://api.github.com'
MESSAGE = 'daily veg price data update'

# 推送清单：远端文件名 -> 本地路径（与小程序 loadRemoteData 拉取的两个文件一致）
FILES = [
    ('prov_data.json', os.path.join(HERE, 'data', 'prov_data.json')),
    ('extra_data.json', os.path.join(HERE, 'data', 'extra_data.json')),
]

DRY_RUN = '--dry-run' in sys.argv


def ctx():
    c = ssl.create_default_context()
    c.check_hostname = False
    c.verify_mode = ssl.CERT_NONE  # 与既有脚本一致的策略，避免本机证书链问题
    return c


CTX = ctx()


def get_token():
    if os.environ.get('GITHUB_VEG_TOKEN'):
        return os.environ['GITHUB_VEG_TOKEN'].strip()
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, encoding='utf-8') as f:
            t = f.read().strip()
        if t:
            return t
    sys.exit('缺少 token：请把 Fine-grained token 写入 .github_token 或设置环境变量 GITHUB_VEG_TOKEN')


def api(path, method='GET', body=None, token=None):
    url = API_ROOT + path
    data = json.dumps(body).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('X-GitHub-Api-Version', '2022-11-28')
    if data is not None:
        req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
            text = r.read().decode('utf-8', 'ignore')
            return r.status, (json.loads(text) if text.strip().startswith(('{', '[')) else text)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'ignore')
    except Exception as e:  # 网络层问题
        return 0, str(e)


def must(step, path, method='GET', body=None, token=None):
    st, res = api(path, method, body, token)
    if st not in (200, 201):
        detail = res if isinstance(res, str) else json.dumps(res, ensure_ascii=False)
        sys.exit(f'{step} 失败 {st}: {detail[:300]}')
    return res


def main():
    token = get_token()
    payload = []
    for name, path in FILES:
        if not os.path.exists(path):
            sys.exit(f'缺少本地文件: {path}')
        with open(path, 'rb') as f:
            raw = f.read()
        payload.append((name, raw))
        print(f'待推送 {name}: {len(raw)} 字节')

    base = f'/repos/{OWNER}/{REPO}'
    ref = must('取分支', f'{base}/git/ref/heads/{BRANCH}', token=token)
    head_sha = ref['object']['sha']
    head = must('取 commit', f'{base}/git/commits/{head_sha}', token=token)
    base_tree = head['tree']['sha']
    print(f'基准 commit={head_sha[:10]} tree={base_tree[:10]}')

    entries = []
    for name, raw in payload:
        blob = must('建 blob', f'{base}/git/blobs', 'POST',
                    {'content': base64.b64encode(raw).decode('ascii'), 'encoding': 'base64'},
                    token)
        entries.append({'path': name, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})

    tree = must('建 tree', f'{base}/git/trees', 'POST',
                {'base_tree': base_tree, 'tree': entries}, token)
    commit = must('建 commit', f'{base}/git/commits', 'POST',
                  {'message': MESSAGE, 'tree': tree['sha'], 'parents': [head_sha]}, token)
    print(f'新 commit={commit["sha"][:10]}')

    if DRY_RUN:
        print('DRY_RUN：未更新远端分支')
        return

    must('更新分支', f'{base}/git/refs/heads/{BRANCH}', 'PATCH',
         {'sha': commit['sha'], 'force': False}, token)
    print(f'推送完成：1 个 commit 更新 {len(entries)} 个文件')
    for name, raw in payload:
        print(f'  {name} {len(raw)} 字节 -> https://{OWNER}.github.io/{REPO}/{name}')


if __name__ == '__main__':
    main()

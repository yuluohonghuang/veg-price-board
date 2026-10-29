# -*- coding: utf-8 -*-
"""用 GitHub API 推送远端数据文件到 veg-price-data 仓库（免浏览器登录态）
用法：python push_remote_json.py
凭据：读取同目录 .github_token（仅存 token 一行）；优先环境变量 GITHUB_VEG_TOKEN
权限：Fine-grained token 只需 veg-price-data 仓库 Contents 读写
"""
import os, sys, json, base64, ssl, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(HERE, '.github_token')
JSON_PATH = os.path.join(HERE, 'data', 'province_retail.json')
OWNER, REPO, PATH = 'yuluohonghuang', 'veg-price-data', 'province_retail.json'
API = f'https://api.github.com/repos/{OWNER}/{REPO}/contents/{PATH}'

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE  # 本机无 requests 时的既有策略

def get_token():
    if os.environ.get('GITHUB_VEG_TOKEN'):
        return os.environ['GITHUB_VEG_TOKEN'].strip()
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, encoding='utf-8') as f:
            t = f.read().strip()
        if t:
            return t
    sys.exit('缺少 token：请把 Fine-grained token 写入 .github_token 或设置环境变量 GITHUB_VEG_TOKEN')

def api_req(url, method='GET', body=None, token=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('X-GitHub-Api-Version', '2022-11-28')
    if body is not None:
        data = json.dumps(body).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
    else:
        data = None
    try:
        with urllib.request.urlopen(req, data=data, timeout=30, context=CTX) as r:
            return r.status, r.read().decode('utf-8', 'ignore')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'ignore')

def main():
    token = get_token()
    # 推送清单：远端文件名 -> 本地路径（小程序 network 拉取三个同构数据文件）
    FILES = [
        ('province_retail.json', os.path.join(HERE, 'data', 'province_retail.json')),
        ('prov_data.json', os.path.join(HERE, 'data', 'prov_data.json')),
        ('extra_data.json', os.path.join(HERE, 'data', 'extra_data.json')),
    ]
    for fname, fpath in FILES:
        if not os.path.exists(fpath):
            print(f'跳过（本地无此文件）: {fpath}')
            continue
        api = f'https://api.github.com/repos/{OWNER}/{REPO}/contents/{fname}'
        with open(fpath, 'rb') as f:
            raw = f.read()
        content_b64 = base64.b64encode(raw).decode('ascii')

        # 取当前文件 sha（已存在则更新需 sha；404 表示首次创建）
        st, body = api_req(api, 'GET', None, token)
        sha = None
        if st == 200:
            sha = json.loads(body).get('sha')
        elif st != 404:
            sys.exit(f'GET {fname} 失败 {st}: {body[:200]}')

        payload = {'message': 'daily veg price data update', 'content': content_b64}
        if sha:
            payload['sha'] = sha
        st, body = api_req(api, 'PUT', payload, token)
        if st in (200, 201):
            j = json.loads(body)
            print(f'推送成功 {fname}: {os.path.getsize(fpath)} 字节')
            print('  commit:', j.get('commit', {}).get('sha', '')[:10])
            print('  URL: https://' + OWNER + '.github.io/' + REPO + '/' + fname)
        else:
            sys.exit(f'PUT {fname} 失败 {st}: {body[:300]}')

if __name__ == '__main__':
    main()

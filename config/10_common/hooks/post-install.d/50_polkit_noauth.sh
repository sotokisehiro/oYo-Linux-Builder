#!/bin/sh
#
# liveユーザーに例外ルールを設定
#
# 【目的】:
#   ライブ環境で “パスワード無しで実行” にするため、polkit に例外ルールを設定 
#
set -e

mkdir -p /etc/polkit-1/rules.d/
cat >/etc/polkit-1/rules.d/10-live-nopasswd.rules <<'RULE'
polkit.addRule(function(action, subject) {
    if (subject.user == "live") {
        return polkit.Result.YES;
    }
});
RULE
chmod 644 /etc/polkit-1/rules.d/10-live-nopasswd.rules


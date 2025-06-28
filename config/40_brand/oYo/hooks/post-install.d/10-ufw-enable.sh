#!/bin/bash
#
# firewallの有効化
#
# 【目的】:
#   - セキュリティ強化のため、デフォルトでfirewallを有効化する
#
set -e

#firewallの有効化
ufw enable


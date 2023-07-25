# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time      :   2022/5/12 16:13
# @Author    :   WenMing
# @Desc      :   
# @Contact   :   736038880@qq.com

# shadowlands-weakauras/classes/paladin 圣骑 cl2
# https://wago.io/shadowlands-weakauras/classes/druid 德鲁伊 cl11
# https://wago.io/shadowlands-weakauras/classes/demon-hunter 恶魔猎手 cl12
# https://wago.io/shadowlands-weakauras/classes/warrior 战士 cl1
# https://wago.io/shadowlands-weakauras/classes/warlock 术士 cl9
# https://wago.io/shadowlands-weakauras/classes/monk 武僧 cl10
# https://wago.io/shadowlands-weakauras/classes/death-knight 死亡骑士 cl6
# https://wago.io/shadowlands-weakauras/classes/mage 法师 cl8
# https://wago.io/shadowlands-weakauras/classes/rogue 盗贼 cl4
# https://wago.io/shadowlands-weakauras/classes/priest 牧师 cl5
# https://wago.io/shadowlands-weakauras/classes/hunter 猎人 cl3
# https://wago.io/shadowlands-weakauras/classes/shaman 萨满 cl7
#
# https://wago.io/shadowlands-weakauras/pve/sepulcher-of-the-first-ones 初诞者圣墓  raidsepulcherfirst
# https://wago.io/shadowlands-weakauras/pve/shadowlands-dungeons 暗影界大米 sldungeon
# https://wago.io/shadowlands-weakauras/pve/timewalking 旧世界副本（时光副本）sltimewalking
# https://wago.io/shadowlands-weakauras/pvp pvp
# https://wago.io/shadowlands-weakauras/class-roles 角色职业 role0
# https://wago.io/shadowlands-weakauras/combat-mechanics 战斗机制 mech
# https://wago.io/shadowlands-weakauras/equipment 装备 tag:equip
# https://wago.io/shadowlands-weakauras/general 通用 tag:gen0
# https://wago.io/shadowlands-weakauras/professions/crafting 制造 tag:prof5
# https://wago.io/shadowlands-weakauras/professions/gathering 采集 tag:prof1
# https://wago.io/shadowlands-weakauras/professions/secondary 第二副业（钓鱼等）tag:prof14
#
#
# https://wago.io/classic-weakauras 经典旧世
# https://wago.io/tbc-weakauras tbc
#
# sl tbc classic
wow_version = {'sl': 1, 'tbc': 2, 'classic': 3}
wow_occupation = {
    'cl2': 'sq', 'cl11': 'xd', 'cl12': 'dh', 'cl1': 'zs', 'cl9': 'ss', 'cl10': 'ws', 'cl6': 'dk', 'cl8': 'fs',
    'cl4': 'dz', 'cl5': 'ms', 'cl3': 'lr', 'cl7': 'sm'
}
wow_talent = {
    'cl2-1': '神圣', 'cl2-2': '防护', 'cl2-3': '惩戒', 'cl11-1': '平衡', 'cl11-2': '野性', 'cl11-3': '守护',
    'cl11-4': '恢复', 'cl12-1': '浩劫', 'cl12-2': '复仇', 'cl1-1': '武器', 'cl1-2': '狂怒', 'cl1-3': '防护',
    'cl9-1': '痛苦', 'cl9-2': '恶魔学识', 'cl9-3': '毁灭', 'cl10-1': '酒仙', 'cl10-2': '织雾', 'cl10-3': '踏风',
    'cl6-1': '鲜血', 'cl6-2': '冰霜', 'cl6-3': '邪恶', 'cl8-1': '奥数', 'cl8-2': '火焰', 'cl8-3': '冰霜',
    'cl4-1': '奇袭', 'cl4-2': '狂徒', 'cl4-3': '敏锐', 'cl5-1': '戒律', 'cl5-2': '神圣', 'cl5-3': '暗影',
    'cl3-1': '野兽控制', 'cl3-2': '射击', 'cl3-3': '生存', 'cl7-1': '元素', 'cl7-2': '增强', 'cl7-3': '恢复'
}
wow_tab = {
    'raidsepulcherfirst': {'type': 3, 'name': '初诞者圣墓'},
    'sldungeon': {'type': 2, 'name': '暗影界五人本'},
    'sltimewalking': {'type': 2, 'name': '时光副本'},
    'pvp': {'type': 2, 'name': 'pvp'},
    'role0': {'type': 1, 'name': '角色职业'},
    'mech': {'type': 3, 'name': '战斗机制'},
    'equip': {'type': 3, 'name': '装备'},
    'gen0': {'type': 3, 'name': '通用'},
    'prof5': {'type': 3, 'name': '制造业'},
    'prof1': {'type': 3, 'name': '采集业'},
    'prof14': {'type': 3, 'name': '第二专业'}
}
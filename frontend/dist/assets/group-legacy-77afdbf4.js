System.register(["./index-legacy-106e4135.js"],(function(t,e){"use strict";var n;return{setters:[function(t){n=t.I}],execute:function(){var e="/group";t("g",{GetGroupById:function(t){return n.post("".concat(e,"/id"),t)},GetMyGroup:function(t){return n.get("".concat(e,"/get"),t)},GetMyJoinGroup:function(t){return n.get("".concat(e,"/a/get"),t)},AddMyGroup:function(t){return n.post("".concat(e,"/post"),t)},UpdateMyGroup:function(t){return n.put("".concat(e,"/put"),t)},DeleteMyGroup:function(t){return n.delete("".concat(e,"/delete"),t)},FindGroup:function(t){return n.get("".concat(e,"/a/get"),t)},SelectGroup:function(t){return n.post("".concat(e,"/a/select"),t)},JoinGroup:function(t){return n.post("".concat(e,"/a/post"),t)},LeaveGroup:function(t){return n.delete("".concat(e,"/a/delete"),t)}})}}}));

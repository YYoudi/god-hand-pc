// Original GPL-3.0-only host launch selection; no game data or addresses.
#pragma once
#include <string>
#include <string_view>

namespace godhand_pc::prototype_execution {
enum class Kind { LegacyDiagnostic, Interactive };
enum class Error { None, UnknownProfile, HiddenInteractive, InteractiveDeadline,
                   MissingUserData, UnqualifiedSdk };
struct Inputs {
    std::string_view profile,visible,seconds,userData;
    bool sdk=false;
};
struct Selection {
    Kind kind=Kind::LegacyDiagnostic;
    Error error=Error::None;
    bool valid()const{return error==Error::None;}
};
// Unset/diagnostic-v1 deliberately hands deadline parsing to the retained
// bounded legacy path. This component never silently upgrades old launches.
inline Selection select(Inputs i) {
    if(i.profile.empty()||i.profile=="diagnostic-v1")return {};
    if(i.profile!="interactive-v1")return {Kind::LegacyDiagnostic,Error::UnknownProfile};
    if(i.visible!="1")return {Kind::Interactive,Error::HiddenInteractive};
    if(!i.seconds.empty()&&i.seconds!="0")return {Kind::Interactive,Error::InteractiveDeadline};
    if(i.userData.empty())return {Kind::Interactive,Error::MissingUserData};
    if(!i.sdk)return {Kind::Interactive,Error::UnqualifiedSdk};
    return {Kind::Interactive,Error::None};
}
inline const char* errorName(Error e) {
    switch(e){
    case Error::None:return "none";case Error::UnknownProfile:return "unknown-profile";
    case Error::HiddenInteractive:return "interactive-must-be-visible";
    case Error::InteractiveDeadline:return "interactive-deadline-must-be-unset-or-zero";
    case Error::MissingUserData:return "interactive-user-data-required";
    case Error::UnqualifiedSdk:return "interactive-qualified-sdk-required";
    }
    return "unknown-error";
}
inline std::string upperAscii(std::string_view name) {
    std::string out(name);for(auto& c:out)if(c>='a'&&c<='z')c=char(c-'a'+'A');return out;
}
inline bool starts(std::string_view s,std::string_view prefix){return s.substr(0,prefix.size())==prefix;}
// Interactive direct-native launches use a small allowlist, not a guessed
// denylist of current diagnostic names. Windows environment names ignore case.
// Never print values of refused variables; they may be private.
inline bool allowedInteractiveVariable(std::string_view name,std::string_view value) {
    const auto key=upperAscii(name);
    if(!starts(key,"PS2X_")&&!starts(key,"PROTOTYPE_")&&!starts(key,"GODHAND_"))return true;
    if(key=="PROTOTYPE_EXECUTION_PROFILE")return value=="interactive-v1";
    if(key=="PROTOTYPE_USERDATA_ROOT")return !value.empty()&&value.find_first_of("\r\n\t")==value.npos;
    if(key=="PROTOTYPE_PROBE_VISIBLE"||key=="PROTOTYPE_DEVELOPER_SHORTCUT")return value=="1";
    if(key=="PROTOTYPE_PROBE_SECONDS")return value=="0";
    if(key=="PROTOTYPE_DEV_PANEL")return value=="controller-v1"||value=="controller-v2";
    if(key=="PROTOTYPE_WINDOW_SHORTCUTS")return value=="edges-v1";
    if(key=="PROTOTYPE_MODULE_CONTROL")return value=="enabled";
    if(key=="PROTOTYPE_VU1_AOT")return value=="0"||value=="1";
    if(key=="PS2X_SIO2_PAD_STATUS")return value=="per-port-v1";
    if(key=="PS2X_FAKE_PADS"||key=="PS2X_VSYNC")return value=="0";
    if(key=="PS2X_AUDIO_MUTE")return value=="0"||value=="1";
    if(key.size()==9&&key.substr(0,8)=="PS2X_PAD"&&key[8]>='2'&&key[8]<='8')return value=="0";
    return false;
}
} // namespace godhand_pc::prototype_execution

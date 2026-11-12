// Original GPL-3.0-only host controller-request model. No game addresses or code.
#pragma once
#include <array>
#include <cstddef>
#include <cmath>
#include <cstdint>
#include <optional>
#include <string_view>

namespace godhand_pc::prototype_controller {
enum class Action { OpenMenu, Up, Down, Left, Right, Circle, Cross, Start, Hide };
enum class Result { Submitted, Refused, UnknownDelivery };
enum class Status { Hidden, Ready, Queued, Submitted, Busy, Expired, Unfocused,
                    ControlsOwnInput, UnsupportedProfile, UnsupportedBindings,
                    ReversedClock, BackendRefused, WriterFault };
struct Context {
    bool verifiedProfile = false;
    bool keyboardOnly = false;
    bool focused = false;
    bool controlsOpen = false;
    bool bridgeBusy = false;
};
inline constexpr std::array<Action,9> actions = {Action::OpenMenu,Action::Up,Action::Down,
    Action::Left,Action::Right,Action::Circle,Action::Cross,Action::Start,Action::Hide};
inline const char* label(Action a) {
    switch(a) {
    case Action::OpenMenu:return "Debug chord";case Action::Up:return "Up";
    case Action::Down:return "Down";case Action::Left:return "Left";
    case Action::Right:return "Right";case Action::Circle:return "Circle";
    case Action::Cross:return "Cross";case Action::Start:return "Start";
    case Action::Hide:return "Hide";
    }
    return "Unsupported";
}
inline std::string_view pulse(Action a) {
    switch(a) {
    case Action::Up:return "up:0.2\n";case Action::Down:return "down:0.2\n";
    case Action::Left:return "left:0.2\n";case Action::Right:return "right:0.2\n";
    case Action::Circle:return "circle:0.2\n";case Action::Cross:return "cross:0.2\n";
    case Action::Start:return "start:0.2\n";
    default:return {};
    }
}
inline const char* message(Status s) {
    switch(s) {
    case Status::Hidden:return "Panel hidden; guest menu unchanged.";
    case Status::Ready:return "Controller requests only; guest menu is NOT acknowledged.";
    case Status::Queued:return "Request queued, not yet sent.";
    case Status::Submitted:return "Controller request submitted; effect NOT acknowledged.";
    case Status::Busy:return "A bounded controller request is still active.";
    case Status::Expired:return "Stale click discarded; no controller request sent.";
    case Status::Unfocused:return "Window unfocused; pending click discarded.";
    case Status::ControlsOwnInput:return "F1 owns input; controller panel closed.";
    case Status::UnsupportedProfile:return "No verified prototype profile; panel disabled.";
    case Status::UnsupportedBindings:return "Experimental panel requires keyboard-only bindings.";
    case Status::ReversedClock:return "Clock reversed; pending click discarded.";
    case Status::BackendRefused:return "Backend refused the request; no success claimed.";
    case Status::WriterFault:return "Writer failed: delivery unknown. Restart this diagnostic run.";
    }
    return "Unknown controller status.";
}
struct Rect {
    float x=0,y=0,width=0,height=0;
    bool contains(float px,float py) const {
        return std::isfinite(px)&&std::isfinite(py)&&px>=x&&py>=y&&px<x+width&&py<y+height;
    }
};
struct Layout {
    Rect background;
    std::array<Rect,9> buttons{};
    bool valid=false;
    std::optional<Action> at(float x,float y) const {
        if(!valid)return {};
        for(size_t n=0;n<buttons.size();++n)if(buttons[n].contains(x,y))return actions[n];
        return {};
    }
};
inline Layout layout(int width,int height);
// Only a press edge is retained. Do not synthesize mouse state, repeats or holds.
class Click {
public:
    bool observe(float x,float y,int width,int height,uint64_t atMs,bool focused) {
        if(pending_||!focused||!layout(width,height).valid||!std::isfinite(x)||!std::isfinite(y))return false;
        pending_=Edge{x,y,width,height,atMs};return true;
    }
    std::optional<Action> take(int width,int height,uint64_t nowMs,bool focused) {
        if(!pending_)return {};
        const auto p=*pending_;pending_.reset();
        if(!focused||width!=p.width||height!=p.height||nowMs<p.at||nowMs-p.at>500)return {};
        return layout(width,height).at(p.x,p.y);
    }
    void clear(){pending_.reset();}
private:
    struct Edge{float x,y;int width,height;uint64_t at;};
    std::optional<Edge> pending_;
};
inline Layout layout(int width,int height) {
    Layout out;
    if(width<480||height<300)return out;
    out.valid=true;out.background={8.0f,float(height-112),float(width-16),104.0f};
    const float buttonWidth=(float(width)-40.0f)/5.0f;
    for(size_t n=0;n<out.buttons.size();++n)
        out.buttons[n]={12.0f+float(n%5)*(buttonWidth+4.0f),float(height-85)+float(n/5)*25.0f,buttonWidth,22.0f};
    return out;
}
class Panel {
public:
    bool show(Context c) {
        if(fault_){status_=Status::WriterFault;return false;}
        if(!eligible(c)){visible_=false;pending_.reset();return false;}
        visible_=true;status_=Status::Ready;return true;
    }
    void hide() { visible_=false;pending_.reset();status_=fault_?Status::WriterFault:Status::Hidden; }
    void writerFault(){fault_=true;pending_.reset();status_=Status::WriterFault;}
    bool request(Action a,uint64_t atMs,Context c) {
        if(!valid(a))return false;
        if(fault_){status_=Status::WriterFault;return false;}
        if(!eligible(c)||!visible_){pending_.reset();return false;}
        if(a==Action::Hide){hide();return true;}
        if(pending_||c.bridgeBusy||atMs<busyUntil_){status_=Status::Busy;return false;}
        pending_=Pending{a,atMs};status_=Status::Queued;return true;
    }
    template<class Dispatch> void tick(uint64_t nowMs,Context c,Dispatch dispatch) {
        if(fault_){status_=Status::WriterFault;pending_.reset();return;}
        if(!eligible(c)) {
            pending_.reset();
            if(c.controlsOpen||!c.verifiedProfile||!c.keyboardOnly)visible_=false;
            return;
        }
        if(!pending_)return;
        const auto p=*pending_;pending_.reset();
        if(nowMs<p.at){status_=Status::ReversedClock;return;}
        if(nowMs-p.at>500){status_=Status::Expired;return;}
        if(!visible_||c.bridgeBusy||nowMs<busyUntil_){status_=Status::Busy;return;}
        const auto result=dispatch(p.action);
        if(result==Result::UnknownDelivery){fault_=true;status_=Status::WriterFault;return;}
        if(result==Result::Refused){status_=Status::BackendRefused;return;}
        lastAction_=p.action;status_=Status::Submitted;
        busyUntil_=nowMs>UINT64_MAX-300?UINT64_MAX:nowMs+300;
    }
    bool visible() const {return visible_;}
    bool faulted() const {return fault_;}
    bool pending() const {return pending_.has_value();}
    bool busy(uint64_t nowMs) const {return pending()||nowMs<busyUntil_;}
    Status status() const {return status_;}
    Action lastAction() const {return lastAction_;}
private:
    struct Pending{Action action;uint64_t at;};
    static bool valid(Action a){for(auto v:actions)if(v==a)return true;return false;}
    bool eligible(Context c) {
        if(!c.verifiedProfile){status_=Status::UnsupportedProfile;return false;}
        if(c.controlsOpen){status_=Status::ControlsOwnInput;return false;}
        if(!c.keyboardOnly){status_=Status::UnsupportedBindings;return false;}
        if(!c.focused){status_=Status::Unfocused;return false;}
        return true;
    }
    bool visible_=false,fault_=false;
    uint64_t busyUntil_=0;
    std::optional<Pending> pending_;
    Status status_=Status::Hidden;
    Action lastAction_=Action::OpenMenu;
};
} // namespace godhand_pc::prototype_controller

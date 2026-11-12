// Original GPL-3.0-only host integration. No guest addresses, calls or memory.
#pragma once
#include "prototype_controller_view.hpp"
#include "ps2_host_input.h"
#include <chrono>
#include <cstdio>

struct GLFWwindow;
using PrototypeMouseCallback=void(*)(GLFWwindow*,int,int,int);
extern "C" GLFWwindow* glfwGetCurrentContext();
extern "C" PrototypeMouseCallback glfwSetMouseButtonCallback(GLFWwindow*,PrototypeMouseCallback);
extern "C" void glfwGetCursorPos(GLFWwindow*,double*,double*);

namespace godhand_pc::prototype_controller {
inline uint64_t monotonicMs(){return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count());}
class NativePanel {
public:
    // Caller must hold the exact-input guard throughout this object's lifetime.
    bool initialize(bool verifiedProfile,bool otherPadsExplicitlyDisabled) {
        if(active_||window_)return false;
        verified_=verifiedProfile;otherPadsDisabled_=otherPadsExplicitlyDisabled;
        if(!verified_||!otherPadsDisabled_)return false;
        window_=glfwGetCurrentContext();if(!window_)return false;
        active_=this;prior_=glfwSetMouseButtonCallback(window_,&mouse);
        std::fprintf(stderr,"PROTOTYPE_CONTROLLER_PANEL initialized=1 callback_chained=%d\n",prior_!=nullptr);
        return true;
    }
    void shutdown() {
        if(window_&&active_==this) {
            auto actual=glfwSetMouseButtonCallback(window_,prior_);
            if(actual!=&mouse)glfwSetMouseButtonCallback(window_,actual);
            active_=nullptr;
        }
        clicks_.clear();panel_.hide();window_=nullptr;
    }
    bool showFromF2() {
        const bool shown=window_&&panel_.show(context(false));
        std::fprintf(stderr,"PROTOTYPE_CONTROLLER_PANEL F2_visible=%d\n",shown);
        return shown;
    }
    void clearPending(){clicks_.clear();}
    bool busy(uint64_t now)const{return window_&&panel_.busy(now);}
    bool faulted()const{return panel_.faulted();}
    void writerFault(){clicks_.clear();panel_.writerFault();}
    template<class Dispatch> void tick(uint64_t now,bool bridgeBusy,Dispatch dispatch) {
        if(!window_)return;
        const auto c=context(bridgeBusy);
        if(c.controlsOpen||!c.focused||!c.keyboardOnly)clicks_.clear();
        if(auto a=clicks_.take(GetScreenWidth(),GetScreenHeight(),now,c.focused))
            (void)panel_.request(*a,now,c);
        panel_.tick(now,c,[&](Action a){
            const auto result=dispatch(a);
            std::fprintf(stderr,"PROTOTYPE_CONTROLLER_REQUEST action=%s result=%d no_effect_ack=1\n",label(a),int(result));
            return result;
        });
        draw(panel_,now,bridgeBusy);
    }
private:
    static bool keyboardOnly() {
        constexpr std::array<const char*,24> keys={"Cross","Circle","Square","Triangle","L1","R1","L2","R2","L3","R3","Start","Select","Up","Down","Left","Right","LUp","LDown","LLeft","LRight","RUp","RDown","RLeft","RRight"};
        for(auto key:keys)for(const auto& b:ps2_host_input::controls::bindings(0,key)) {
            if(b.empty())continue;
            if(b.compare(0,9,"Keyboard/")!=0||ps2_host_input::controls::kindOf(b)!=ps2_host_input::controls::Kind::Keys)return false;
        }
        return true;
    }
    Context context(bool bridgeBusy) const {
        return {verified_,otherPadsDisabled_&&keyboardOnly(),IsWindowFocused(),ps2_host_input::overlayOpen(),bridgeBusy};
    }
    static void mouse(GLFWwindow* w,int button,int action,int mods) {
        auto* self=active_;if(!self)return;
        if(self->prior_)self->prior_(w,button,action,mods);
        if(w!=self->window_||button!=MOUSE_BUTTON_LEFT||action!=1||!self->panel_.visible())return;
        const auto c=self->context(false);
        if(!c.focused||c.controlsOpen||!c.keyboardOnly||!c.verifiedProfile){self->clicks_.clear();return;}
        double x=0,y=0;glfwGetCursorPos(w,&x,&y);
        const bool queued=self->clicks_.observe(float(x),float(y),GetScreenWidth(),GetScreenHeight(),monotonicMs(),c.focused);
        std::fprintf(stderr,"PROTOTYPE_CONTROLLER_CLICK x=%.3f y=%.3f width=%d height=%d queued=%d\n",x,y,GetScreenWidth(),GetScreenHeight(),queued);
    }
    inline static NativePanel* active_=nullptr;
    GLFWwindow* window_=nullptr;
    PrototypeMouseCallback prior_=nullptr;
    bool verified_=false,otherPadsDisabled_=false;
    Panel panel_;
    Click clicks_;
};
} // namespace godhand_pc::prototype_controller

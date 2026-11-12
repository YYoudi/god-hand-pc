// Original GPL-3.0-only optional host view. Raylib is a separately pinned dependency.
#pragma once
#include "prototype_controller_panel.hpp"
#include <raylib.h>

namespace godhand_pc::prototype_controller {
inline void draw(const Panel& panel,uint64_t nowMs,bool bridgeBusy,ControlSet controls=ControlSet::DigitalV1) {
    if(!panel.visible())return;
    const auto positions=layout(GetScreenWidth(),GetScreenHeight());
    if(!positions.valid)return;
    const auto r=[](Rect a){return Rectangle{a.x,a.y,a.width,a.height};};
    const bool disabled=panel.faulted()||panel.busy(nowMs)||bridgeBusy;
    if(controls==ControlSet::LeftStickV2) {
        const auto sticks=stickLayout(GetScreenWidth(),GetScreenHeight());
        DrawRectangleRec(r(sticks.background),Color{20,23,27,245});
        DrawRectangleLinesEx(r(sticks.background),1.0f,Color{125,133,141,255});
        DrawText("Left stick: bounded 200 ms requests",12,GetScreenHeight()-167,14,Color{230,231,233,255});
        for(size_t n=0;n<sticks.buttons.size();++n){const auto b=sticks.buttons[n];
            DrawRectangleRec(r(b),disabled?Color{43,46,51,255}:Color{67,75,84,255});
            DrawText(label(stickActions[n]),int(b.x+5),int(b.y+4),14,disabled?Color{137,143,150,255}:Color{245,245,245,255});
        }
    }
    DrawRectangleRec(r(positions.background),Color{20,23,27,245});
    DrawRectangleLinesEx(r(positions.background),1.0f,Color{125,133,141,255});
    DrawText("Prototype controller requests (experimental)",12,GetScreenHeight()-107,14,Color{230,231,233,255});
    for(size_t n=0;n<positions.buttons.size();++n) {
        const auto a=actions[n];const auto b=positions.buttons[n];
        const bool muted=disabled&&a!=Action::Hide;
        DrawRectangleRec(r(b),muted?Color{43,46,51,255}:Color{67,75,84,255});
        DrawText(label(a),int(b.x+5),int(b.y+4),14,muted?Color{137,143,150,255}:Color{245,245,245,255});
    }
    DrawText(message(panel.status()),12,GetScreenHeight()-32,10,Color{216,219,224,255});
    DrawText("Circle: confirm. Cross: back. Hide: panel only. Game is NOT paused by this panel.",12,GetScreenHeight()-18,10,Color{173,181,190,255});
}
} // namespace godhand_pc::prototype_controller

// Original GPL-3.0-only bounded append-log framing; no game code or addresses.
#pragma once
#include <cstddef>
#include <istream>
#include <string>
#include <utility>

namespace godhand_pc::command_lines {
enum class Result { Pending, Line, Fault };
class Reader {
public:
    // Open/seekable stream supplied anew on each poll. Commit only complete LF
    // records; a concurrently appended partial record is never a command.
    Result poll(std::istream& input, std::string& output) {
        output.clear();
        if(fault_)return Result::Fault;
        input.clear();input.seekg(0,std::ios::end);
        const auto end=input.tellg();
        if(end<offset_)return fail();
        input.seekg(offset_,std::ios::beg);
        if(!input)return fail();
        std::string line;
        for(std::size_t i=0;i<maxPayload+2;++i){
            char c=0;
            if(!input.get(c))return input.eof()?Result::Pending:fail();
            if(c=='\n'){
                if(!line.empty()&&line.back()=='\r')line.pop_back();
                if(line.size()>maxPayload)return fail();
                for(unsigned char b:line)if(b<32||b>126)return fail();
                const auto next=input.tellg();
                if(next<offset_)return fail();
                offset_=next;output=std::move(line);return Result::Line;
            }
            line.push_back(c);
        }
        return fail();
    }
    std::streamoff offset()const{return offset_;}
    static constexpr std::size_t maxPayload=256;
private:
    Result fail(){fault_=true;return Result::Fault;}
    std::streamoff offset_=0;
    bool fault_=false;
};
} // namespace godhand_pc::command_lines

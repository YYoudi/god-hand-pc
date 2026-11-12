// Original GPL-3.0-only bounded observation utility. No game addresses/data.
#pragma once
#include <cstddef>
#include <cstdint>
#include <unordered_set>
#include <vector>

namespace godhand_pc::diagnostic_chain {
enum class Status { Complete, InvalidBudget, Limit, Cycle, Unreadable };
struct Result {
    Status status=Status::Complete;
    std::vector<std::uint32_t> nodes;
};
// Opaque IDs, not an allocator/ownership model. Complete means only that the
// supplied links reached zero. It is NOT proof of deallocation, memory safety,
// a free block, hardware fidelity or a successful guest action. The caller's
// reader determines provenance; this helper never edits IDs or supplied memory.
template<class ReadNext>
Result walk(std::uint32_t first,std::size_t budget,ReadNext readNext) {
    Result result;
    if(budget==0||budget>4096){result.status=Status::InvalidBudget;return result;}
    std::unordered_set<std::uint32_t> seen;
    auto current=first;
    while(current!=0) {
        if(seen.find(current)!=seen.end()){result.status=Status::Cycle;return result;}
        if(result.nodes.size()>=budget){result.status=Status::Limit;return result;}
        std::uint32_t next=0;
        if(!readNext(current,next)){result.status=Status::Unreadable;return result;}
        seen.insert(current);result.nodes.push_back(current);current=next;
    }
    return result;
}
inline const char* name(Status status) {
    switch(status) {
    case Status::Complete:return "complete-links-only";
    case Status::InvalidBudget:return "invalid-budget";
    case Status::Limit:return "limit";
    case Status::Cycle:return "cycle";
    case Status::Unreadable:return "unreadable";
    }
    return "unknown";
}
} // namespace godhand_pc::diagnostic_chain

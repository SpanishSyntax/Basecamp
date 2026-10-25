const std = @import("std");

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    try stdout.print("⛺ [basecamp] Zig environment initialized for {s}!\n", .{"__PROJECT_NAME__"});
}

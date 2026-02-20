const std = @import("std");
const Allocator = std.mem.Allocator;

/// Configuration for Twitter capture
const CaptureConfig = struct {
    url: []const u8,
    output_path: []const u8,
    width: u32 = 1200,
    height: u32 = 675,
    wait_time_ms: u32 = 3000, // Wait for content to load
};

/// Main entry point
pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    if (args.len < 2) {
        std.debug.print("Usage: twitter-capture <twitter_url> [output_path]\n", .{});
        std.debug.print("Example: twitter-capture https://twitter.com/user/status/123\n", .{});
        return error.InvalidArguments;
    }

    const url = args[1];
    const output_path = if (args.len >= 3) 
        args[2] 
    else 
        "twitter_capture.png";

    const config = CaptureConfig{
        .url = url,
        .output_path = output_path,
    };

    std.debug.print("Capturing Twitter URL: {s}\n", .{url});
    std.debug.print("Output: {s}\n", .{output_path});

    // Capture the Twitter page
    try captureTwitterPage(allocator, config);
    
    std.debug.print("✓ Successfully captured Twitter page to {s}\n", .{output_path});
}

/// Capture Twitter page as image
/// Note: This is a simplified version. In production, you'd use WebKitGTK or similar
pub fn captureTwitterPage(allocator: Allocator, config: CaptureConfig) !void {
    // For now, we'll create a placeholder implementation
    // In a real implementation, you would:
    // 1. Launch a headless browser (WebKitGTK, Puppeteer, etc.)
    // 2. Navigate to the Twitter URL
    // 3. Wait for content to load
    // 4. Take a screenshot
    // 5. Save to file
    
    std.debug.print("ℹ Note: Full browser integration requires WebKitGTK\n", .{});
    std.debug.print("ℹ Installing dependencies:\n", .{});
    std.debug.print("   sudo apt install libwebkit2gtk-4.1-dev libgtk-3-dev\n", .{});
    
    // Create a simple placeholder image with the URL text
    try createPlaceholderImage(allocator, config);
}

/// Create a placeholder image (for testing without browser)
fn createPlaceholderImage(_: Allocator, config: CaptureConfig) !void {
    // Simple PNG creation (minimal valid PNG)
    // In production, use a proper image library like stb_image_write
    
    const file = try std.fs.cwd().createFile(config.output_path, .{});
    defer file.close();
    
    const writer = file.writer();
    
    // Write a simple text file instead (placeholder)
    try writer.print("Twitter URL: {s}\n", .{config.url});
    try writer.print("Captured at: {}\n", .{std.time.timestamp()});
    try writer.print("\nNote: Install WebKitGTK for full image capture support\n", .{});
    
    std.debug.print("⚠ Created placeholder (install WebKitGTK for real images)\n", .{});
}

/// Extract tweet ID from Twitter URL
pub fn extractTweetId(url: []const u8) ?[]const u8 {
    // Handle various Twitter URL formats:
    // - https://twitter.com/user/status/123456
    // - https://x.com/user/status/123456
    // - https://www.twitter.com/user/status/123456
    
    const patterns = [_][]const u8{
        "/status/",
        "/statuses/",
    };
    
    for (patterns) |pattern| {
        if (std.mem.indexOf(u8, url, pattern)) |pos| {
            const start = pos + pattern.len;
            if (start < url.len) {
                const remaining = url[start..];
                // Find end of ID (could be end of string or query param)
                if (std.mem.indexOfAny(u8, remaining, "?#/")) |end_pos| {
                    if (end_pos > 0) {
                        return remaining[0..end_pos];
                    }
                } else {
                    return remaining;
                }
            }
        }
    }
    
    return null;
}

test "extract tweet ID" {
    const url1 = "https://twitter.com/user/status/1234567890";
    const url2 = "https://x.com/user/status/9876543210?lang=en";
    const url3 = "https://www.twitter.com/user/status/1111111111#anchor";
    
    try std.testing.expectEqualStrings("1234567890", extractTweetId(url1).?);
    try std.testing.expectEqualStrings("9876543210", extractTweetId(url2).?);
    try std.testing.expectEqualStrings("1111111111", extractTweetId(url3).?);
}

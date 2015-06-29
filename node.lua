gl.setup(NATIVE_WIDTH, NATIVE_HEIGHT)

node.alias "videowall"

local json = require 'json'
local raw = sys.get_ext "raw_video"

local player = (function()
    local res, old_res, next_res, master
    node.event("connect", function(new_master)
        if master then node.client_disconnect(master) end
        master = new_master
        print("master connected")
    end)

    node.event("disconnect", function(client)
        assert(client == master)
        print("master disconnected")
        master = nil
    end)

    -- {"cmd": "load", "filename": "optical.mp4"}
    -- {"cmd": "start"}
    node.event("input", function(pkt, client)
        assert(client == master)
        pkt = json.decode(pkt)
        pp(pkt)
        if pkt.cmd == "load" then
            if next_res then next_res:dispose() end
            next_res = raw.load_video(pkt.filename, false, false, true)
        elseif pkt.cmd == "start" then
            old_res = res
            res = next_res
            next_res = nil
            res:start()
        end
    end)

    local function send_state(state)
        if master then
            node.client_write(master, state)
        end
    end

    local function tick()
        if next_res then
            send_state(next_res:state())
        elseif res then
            res:target(0, 0, NATIVE_WIDTH, NATIVE_HEIGHT)
            send_state(res:state())
        else
            send_state("none")
        end

        if old_res then 
            old_res:dispose()
        end
    end

    return {
        tick = tick;
    }
end)()

function node.render()
    gl.clear(0,0,0,0)
    player.tick()
end

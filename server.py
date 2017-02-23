from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import urlparse
import json
import core

class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        params = {}
        name_values = parsed_path.query.split(u'&')
        for name_value in name_values:
            index = name_value.find(u'=')
            name = name_value[:index]
            value = name_value[index+1:]
            params[name] = value
        stones = [int(i) if i != "2" else -1 for i in params["stones"][:]]
        pos = int(params["pos"])
        stone = int(params["stone"])

        board = core.Board(stones=stones)
        board.move(pos, stone)
        pre_stones = "".join([str(i) if i >= 0 else "2" for i in board.stones])
        print pre_stones
        epos = player.move(board, -stone)
        print epos
        movable_pos = board.calc_movable_pos(stone)
        res = json.dumps({"movables": "".join(["1" if i in movable_pos else "0" for i in xrange(0, 64)]),
                          "stones": "".join([str(i) if i >= 0 else "2" for i in board.stones]),
                          "pre_stones": pre_stones,
                          "pos": epos,
                          "gameover": board.check_gameover()},
                          sort_keys=False, indent=4)

        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(res)
        return

def decode_stones(stones_code):
    pass

def encode_stones(stones):
    pass


if __name__ == '__main__':

    evaluator = core.Evaluator()
    player = core.Player(evaluator)

    httpd = HTTPServer(('localhost', 8080), GetHandler)
    httpd.serve_forever()

import importlib.util, sys
sys.dont_write_bytecode = True
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
import os
from pathlib import Path
R = str(Path(os.environ.get("MYCEL_REPO", Path.home() / "repos/sylvan-stack/mycel_deprecated_v1")) / "mycel/knowledge") + "/"
cc = load("code_chunker_probe", R + "code_chunker.py")
def show(chunks):
    for c in chunks:
        print(f"  {c['symbol']!r:30} {c['kind']:10} {c['line_start']:>3}-{c['line_end']:<3} {c['text'][:60]!r}")

ts = '''import { a } from "./a";
export { b } from "./b";

export function plain(x: number): number {
  return x;
}

function overload(a: string): void;
function overload(a: number): void;
function overload(a: any): void {}

export const arrow = async (q: string) => {
  return q;
};

const wrapped = observer(() => {
  return null;
});

const config = { k: 1 };
let one = () => 1, two = () => 2;

@Injectable()
export class Service extends Base {
  private n = 0;

  constructor(private dep: Dep) { super(); }

  @Get("/x")
  @Auth()
  async handle(): Promise<void> {}

  field = () => 3;

  get value() { return this.n; }
  set value(v) { this.n = v; }

  [Symbol.iterator]() {}
}

export interface Shape { w: number }
type Alias = string | number;
export enum Color { Red, Green }
export namespace Outer { export const z = 1; }
namespace Bare { export const z = 1; }
declare module "x" { const y: number; }
declare function amb(): void;
export abstract class Abs { abstract go(): void; stay() {} }
export default function () { return 1; }
class NoMethods { a = 1 }
function* gen() { yield 1; }
doSomething();
'''
print("== ts"); show(cc.chunk_code("svc/thing.ts", ts))

tsx = '''export const Card = ({ t }: { t: string }) => <div>{t}</div>;
export default class extends Base { m() {} }
const { p, q } = useThing();
export const Memo = memo(function Inner() { return <i/>; });
export default Card;
'''
print("== tsx"); show(cc.chunk_code("ui/card.tsx", tsx))

js = '''const x = require("x");
module.exports = function () {};
function f() {}
var g = function () {};
class C { static s() {} m() {} }
export default async function named() {}
'''
print("== js"); show(cc.chunk_code("lib/x.js", js))
print("== ts syntax error"); show(cc.chunk_code("bad.ts", "export function ( {\n  class\n}\nfunction ok() {}\n"))
print("== ts empty"); show(cc.chunk_code("e.ts", ""))
print("== ts one-line class"); show(cc.chunk_code("o.ts", "class A { m() {} }\n"))

// prosthesisAudio.cc
// for help see : https://nodejs.org/api/addons.html
// and http://www.benfarrell.com/2013/01/03/c-and-node-js-an-unholy-combination-but-oh-so-right/

#include <node.h>

namespace audio 
{

using v8::FunctionCallbackInfo;
using v8::Isolate;
using v8::Local;
using v8::Object;
using v8::String;
using v8::Value;

void Method(const FunctionCallbackInfo<Value>& args) 
{
  Isolate* isolate = args.GetIsolate();
  args.GetReturnValue().Set(String::NewFromUtf8(isolate, "world"));
}

void init(Local<Object> exports) 
{
  NODE_SET_METHOD(exports, "hello", Method);
}

// The module_name must match the filename of the final binary (excluding the .node suffix).
// In the prosthesisAudio.cc example, then, the initialization function is init and the module name is prosthesisAudio
// Once the source code has been written, it must be compiled into the binary prosthesisAudio.node 
NODE_MODULE(prosthesisAudio, init)

}  // namespace audio
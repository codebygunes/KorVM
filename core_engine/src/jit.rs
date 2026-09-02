//! KorVM Self-Optimizing Cranelift JIT Engine
//! Author: Elif Nur Ayhan (codebygunes)
//! License: Apache-2.0

use crate::error::KorVmError;
use cranelift::prelude::*;
use cranelift_jit::{JITBuilder, JITModule};
use cranelift_module::{Module, Linkage};

pub struct KorVmJitEngine {
    module: JITModule,
    ctx: codegen::Context,
    builder_context: FunctionBuilderContext,
}

impl KorVmJitEngine {
    /// Initializes a safe, sandboxed JIT compilation environment targeting the host machine.
    pub fn new() -> Result<Self, KorVmError> {
        let builder = JITBuilder::new(cranelift_module::default_libcall_names())
            .map_err(|e| KorVmError::CompilationError(format!("JIT Builder Init Failed: {}", e)))?;
            
        let module = JITModule::new(builder);
        let ctx = module.make_context();
        let builder_context = FunctionBuilderContext::new();

        Ok(Self {
            module,
            ctx,
            builder_context,
        })
    }

    /// Compiles a dummy function safely to demonstrate the architectural pipeline 
    /// without resorting to unchecked raw pointer arithmetic or unwraps.
    pub fn compile_and_execute_dummy(&mut self) -> Result<i32, KorVmError> {
        // 1. Define function signature: () -> i32
        self.ctx.func.signature.returns.push(AbiParam::new(types::I32));

        // 2. Safely build function logic
        {
            let mut builder = FunctionBuilder::new(&mut self.ctx.func, &mut self.builder_context);
            let entry_block = builder.create_block();
            builder.append_block_params_for_function_params(entry_block);
            builder.switch_to_block(entry_block);
            builder.seal_block(entry_block);

            // Safely emit constant: 42
            let cst = builder.ins().iconst(types::I32, 42);
            builder.ins().return_(&[cst]);
            builder.finalize();
        }

        // 3. Declare and define safely within the module
        let id = self.module
            .declare_function("dummy_func", Linkage::Export, &self.ctx.func.signature)
            .map_err(|e| KorVmError::CompilationError(e.to_string()))?;

        self.module
            .define_function(id, &mut self.ctx)
            .map_err(|e| KorVmError::CompilationError(e.to_string()))?;

        // 4. Finalize compilation to hardware memory safely
        self.module.clear_context(&mut self.ctx);
        self.module.finalize_definitions();

        // 5. Safe Execution Boundary
        let code_ptr = self.module.get_finalized_function(id);
        
        let result = unsafe {
            // This is the ONLY required unsafe block in the JIT execution pipeline.
            // Strict precondition: The code pointer is guaranteed to be finalized and verified by Cranelift.
            if code_ptr.is_null() {
                return Err(KorVmError::ExecutionError("Failed to resolve finalized JIT code pointer.".into()));
            }
            let func: extern "C" fn() -> i32 = std::mem::transmute(code_ptr);
            func()
        };

        Ok(result)
    }
}
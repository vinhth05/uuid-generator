import multiprocessing
import sys
import os

def main():
    # Freeze support is critical for PyInstaller when using multiprocessing
    # Though we used threading in our implementation, it's good practice for Windows executables
    multiprocessing.freeze_support()
    
    try:
        from gui.app import App
        from utils.logger import logger
        
        logger.info("Application starting...")
        app = App()
        app.mainloop()
        logger.info("Application closed.")
        
    except Exception as e:
        import traceback
        import tkinter.messagebox
        error_msg = f"Fatal error during startup:\n{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        # Attempt to show a graphical error if logger/gui fails
        try:
            tkinter.messagebox.showerror("Fatal Error", error_msg)
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()

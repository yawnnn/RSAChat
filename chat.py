import tkinter as tk

# doesn't do much, it's just to divide GUI from program's logic 
class Chat:

	on_close_callback = None

	#self.chat.configure(background='#424242')

	def __init__(self):
		self.chat = tk.Tk()
		self.msgFrame = tk.Frame(self.chat)
		self.scrollbar = tk.Scrollbar(self.msgFrame)
		self.msg = tk.StringVar()
		self.msgBox = tk.Listbox(self.msgFrame)
		self.label = tk.Label(self.chat)
		self.textBox = tk.Entry(self.chat)

	def start(self, msg_callback, on_close_callback):
		self.msgBox.configure(height=10, width=60, yscrollcommand=self.scrollbar.set)
		self.label.configure(text="Text")
		self.textBox.configure(textvariable=self.msg, width=55)

		self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		self.msgBox.pack(side=tk.LEFT, fill=tk.BOTH)
		self.msgFrame.pack()

		self.label.pack(side=tk.LEFT)
		self.textBox.bind("<Return>", msg_callback)
		self.textBox.pack(side=tk.RIGHT)

		self.chat.protocol("WM_DELETE_WINDOW", self.close)
		self.on_close_callback = on_close_callback

		self.chat.mainloop()

	def close(self):
		self.on_close_callback()
		self.chat.quit()

	def showMessage(self, msg):
		self.msgBox.insert(tk.END, msg)

	def getMessage(self):
		msg = self.msg.get()
		self.msg.set('')
		return msg

if __name__ == "__main__":

	chat = Chat()
	chat.start(lambda: True, lambda: True)
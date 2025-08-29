from pyllama import Chat
from pyllama.dockerpy import PythonToolKit


toolkit = PythonToolKit()
#toolkit.install_python()
chat = Chat()
#chat = Chat("devstral:latest")
for tool in toolkit.get_tools():
    chat.add_tool(tool)

chat.system("Never perform calculations on your own. Always use your tools to write code to inform your answers when possible, especially when those questions involve calculations.")
#chat.prompt("If the moon were to suddenly stop in its orbit, how long would it take to fall to earth?")
toolkit.write_file("circuit.qasm", """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[3];
        h q[0];
        cp(1.5707963267948966) q[1], q[0];
        h q[1];
        cp(0.7853981633974483) q[2], q[0];
        cp(1.5707963267948966) q[2], q[1];
        h q[2];
        swap q[0], q[2];
        h q[0];
        cp(-1.5707963267948966) q[1], q[0];
        h q[1];
        cp(-0.7853981633974483) q[2], q[0];
        cp(-1.5707963267948966) q[2], q[1];
        h q[2];
        swap q[0], q[2];
        """
                   )
chat.prompt("I have a quantum circuit in OPENQASM 2.0 format saved as circuit.qasm. I would like to reduce the number of CNOT gates in this circuit. Can you perform this circuit optimziation? Let me know what the final CNOT count you arrive at is.")
chat.print()

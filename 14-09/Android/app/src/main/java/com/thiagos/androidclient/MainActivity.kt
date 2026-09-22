package com.thiagos.androidclient

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.io.PrintWriter
import java.net.InetSocketAddress
import java.net.Socket

class MainActivity : AppCompatActivity() {

    private lateinit var edtNum1: EditText
    private lateinit var edtNum2: EditText
    private lateinit var spnOperacao: Spinner
    private lateinit var btnCalcular: Button
    private lateinit var txtResultado: TextView

    companion object {
        private const val IP_SERVIDOR = "10.0.2.2"
        private const val PORTA = 9000
    }

    override fun onCreate(
        savedInstanceState: Bundle?
    ) {
        super.onCreate(savedInstanceState)

        setContentView(
            R.layout.activity_main
        )

        edtNum1 = findViewById(
            R.id.edtNum1
        )

        edtNum2 = findViewById(
            R.id.edtNum2
        )

        spnOperacao = findViewById(
            R.id.spnOperacao
        )

        btnCalcular = findViewById(
            R.id.btnCalcular
        )

        txtResultado = findViewById(
            R.id.txtResultado
        )

        btnCalcular.setOnClickListener {

            val textoNum1 =
                edtNum1.text.toString()

            val textoNum2 =
                edtNum2.text.toString()

            if (
                textoNum1.isEmpty() ||
                textoNum2.isEmpty()
            ) {

                Toast.makeText(
                    this,
                    "Informe os dois números.",
                    Toast.LENGTH_SHORT
                ).show()

                return@setOnClickListener
            }

            calcular(
                textoNum1.toInt(),
                textoNum2.toInt(),
                spnOperacao
                    .selectedItem
                    .toString()
            )
        }
    }

    private fun calcular(
        num1: Int,
        num2: Int,
        operacao: String
    ) {

        btnCalcular.isEnabled = false
        txtResultado.text = "Conectando..."

        lifecycleScope.launch {

            try {

                val resposta = withContext(Dispatchers.IO) {

                    val socket = Socket()

                    socket.connect(
                        InetSocketAddress(
                            "localhost",
                            9000
                        ),
                        3000
                    )

                    socket.soTimeout = 5000

                    val saida = PrintWriter(
                        OutputStreamWriter(
                            socket.getOutputStream(),
                            Charsets.UTF_8
                        ),
                        true
                    )

                    val entrada = BufferedReader(
                        InputStreamReader(
                            socket.getInputStream(),
                            Charsets.UTF_8
                        )
                    )

                    val json = """
                    {"operacao":"$operacao","num1":$num1,"num2":$num2}
                """.trimIndent()

                    println("ENVIANDO: $json")

                    saida.println(json)
                    saida.flush()

                    println("AGUARDANDO RESPOSTA...")

                    val respostaServidor = entrada.readLine()

                    println("RESPOSTA: $respostaServidor")

                    socket.close()

                    respostaServidor
                }

                txtResultado.text =
                    "Resposta: $resposta"

            } catch (e: Exception) {

                txtResultado.text =
                    "ERRO: ${e.javaClass.simpleName}\n${e.message}"

            } finally {

                btnCalcular.isEnabled = true
            }
        }
    }
}
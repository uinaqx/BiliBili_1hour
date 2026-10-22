package lessons.kt_10_03
import java.io.File
fun main() {
    val file = File("scores.txt")
    file.writeText("小林,85\n小陈,92")
    val text = file.readText()
    println(text)
}

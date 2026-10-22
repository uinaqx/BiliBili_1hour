package lessons.kt_10_01
fun main() {
    val text = "hello"
    try {
        println(text.toInt())
    } catch (e: NumberFormatException) {
        println("请输入整数")
    }
}

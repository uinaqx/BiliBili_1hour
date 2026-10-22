package lessons.kt_10_06
fun main() {
    val text = "hello"
    val score = text.toIntOrNull() ?: 0
    println("你的成绩：$score")
}

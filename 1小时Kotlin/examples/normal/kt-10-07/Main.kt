package lessons.kt_10_07
fun main() {
    val text = "hello"
    val score = text.toIntOrNull()
    when {
        score == null -> println("请输入整数")
        score !in 0..100 -> println("成绩超出范围")
        else -> println("你的成绩：$score")
    }
}

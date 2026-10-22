package lessons.kt_04_03
fun main() {
    val score = 88
    val level = when {
        score >= 90 -> "优秀"
        score >= 60 -> "及格"
        else -> "未及格"
    }
    println(level)
}

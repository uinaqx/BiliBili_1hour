package lessons.kt_10_02
fun checkScore(score: Int) {
    require(score in 0..100) { "成绩应在 0 到 100 之间" }
}
fun main() {
    try {
        checkScore(120)
    } catch (e: IllegalArgumentException) {
        println("成绩不合法")
    }
}

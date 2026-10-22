package lessons.kt_03_03
fun main() {
    val score = 85
    val attended = true
    println(score >= 60)
    println(score >= 60 && attended)
    println(score < 60 || !attended)
}

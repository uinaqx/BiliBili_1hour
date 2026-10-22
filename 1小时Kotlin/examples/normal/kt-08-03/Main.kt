package lessons.kt_08_03
class Student(val name: String) {
    private var score = 0
    fun updateScore(value: Int) {
        if (value in 0..100) score = value
    }
    fun currentScore(): Int = score
}
fun main() {
    val s = Student("小林")
    s.updateScore(85)
    println(s.currentScore())
}

package lessons.kt_08_05
data class Student(val name: String, val score: Int)
fun main() {
    val original = Student("小林", 80)
    val corrected = original.copy(score = 85)
    println(original.score)
    println(corrected.score)
}

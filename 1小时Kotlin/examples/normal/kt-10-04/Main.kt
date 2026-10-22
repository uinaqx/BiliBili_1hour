package lessons.kt_10_04
data class Student(val name: String, val score: Int)
fun main() {
    val students = listOf(
        Student("小林", 85), Student("小陈", 55),
        Student("小王", 90)
    )
    val passed = students.filter { it.score >= 60 }
    for (s in passed) println("${s.name}：${s.score}")
}

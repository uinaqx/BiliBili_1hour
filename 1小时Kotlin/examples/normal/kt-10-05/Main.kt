package lessons.kt_10_05
data class Student(val name: String, val score: Int)
fun average(students: List<Student>): Double? {
    if (students.isEmpty()) return null
    return students.map { it.score }.average()
}
fun main() {
    val students = listOf(
        Student("小林", 80), Student("小陈", 90)
    )
    println(average(students) ?: "暂无成绩")
    println(average(emptyList()) ?: "暂无成绩")
}

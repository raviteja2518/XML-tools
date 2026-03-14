export default function HeadPage(){

  return(

    <div style={styles.page}>

      <h2 style={styles.title}>
        Head Reference Tool
      </h2>

      <p style={styles.subtitle}>
        This tool processes the head section of references.
      </p>

    </div>

  )

}

const styles:any={

 page:{
  maxWidth:"900px",
  margin:"40px auto",
  padding:"40px",
  background:"#ffffff",
  borderRadius:"16px",
  boxShadow:"0 10px 30px rgba(0,0,0,0.08)"
 },

 title:{
  textAlign:"center",
  fontSize:"28px",
  marginBottom:"10px"
 },

 subtitle:{
  textAlign:"center",
  color:"#475569"
 }

}
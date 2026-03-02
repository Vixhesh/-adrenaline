const express=require("express");
const jwt=require("jsonwebtoken");
const app= express();
const secret="supersecret";
app.use(express.static("public"));
app.get('/' ,(req,res)=>{
    const token=req.query.token;
    try{
        jwt.verify(token.secret)
        res.sendFile(__dirname+"/public/index.html");

    }catch{
        res.status(401).send("Unauthorized");
    }

});
app.listen(3000, () => console.log("Game server on 3000"));
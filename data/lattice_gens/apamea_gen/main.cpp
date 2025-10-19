#include "Part.h"
#include "Vect.h"
#include <vector>
#include <array>
#include <string>
#include "PartArray.h"

static int hCells = 5;
static int vCells = 5;

static int unitCellSizeX = 4;
static int unitCellSizeY = 4;

int main(){

    PartArray unitCellEven,unitCellOdd,unitCell;
    unitCellEven.load("../unitCellEven.mfsys");
    unitCellOdd.load("../unitCellOdd.mfsys");

    PartArray sys;
    Part *temp;

    bool mayBeInserted;
    int totSpins = 0;
    for (int i=0;i<vCells;i++){
        for (int j=0;j<hCells;j++){
            if ((i+j)%2==0)
                unitCell = unitCellEven;
            else
                unitCell = unitCellOdd;

            for (auto p : unitCell.parts){
                temp = new Part();
                temp->pos.setXYZ(p->pos.x + j*unitCellSizeX, p->pos.y + i*unitCellSizeX,0);
                temp->m = Vect(p->m);
                sys.insert(temp);
            }
        }
    }

    sys.save(std::string("apamea_")+std::to_string(vCells)+"_"+std::to_string(hCells)+".mfsys");


    return 0;
}